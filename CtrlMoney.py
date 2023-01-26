import sys
import datetime as dt

from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QLabel
from PyQt5.QtSql import QSqlDatabase, QSqlQueryModel, QSqlQuery

from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtGui import QPixmap

import Expense
from Expense import COLOR_EXPENSE, COLOR_INCOME, setRUBFormat


# Класс виджета о программе
class DAbout(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Зададим размер и положение нашего виджета,
        self.setFixedSize(500, 200)

        self.pixmap = QPixmap('forms/background.png')
        self.image = QLabel(self)
        self.image.move(0, 0)
        # Отображаем содержимое QPixmap в объекте QLabel
        self.image.setPixmap(self.pixmap)

        self.label = QLabel(self)

        # Выводим на экран результат работы функции file
        self.label.setText(self.fromFile())
        self.label.setTextFormat(1)
        self.label.move(40, 30)

        # А также его заголовок
        self.setWindowTitle('О программе...')

    # Берем ифнформацию из файла
    def fromFile(self):
        with open('forms/version', encoding='UTF8', mode='rt') as f:
            text_about_the_program = f.read()
            return text_about_the_program


# Класс главного окна
class CtrlMoney(QMainWindow):
    def __init__(self):
        super().__init__()

        self.sum_expense = 0.00
        self.sum_income = 0.00
        self.sum_balance = 0.00

        self.initUI()
        self.initDB()
        self.initSignals()

    # Инициализация базы данных
    def initDB(self):
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('db/expenses.db')
        self.db.open()

    # Инициализация интерфейса
    def initUI(self):
        uic.loadUi('forms/FCtrlMoney.ui', self)

        self.editExpense.setStyleSheet(f'color: {COLOR_EXPENSE};')
        self.editIncome.setStyleSheet(f'color: {COLOR_INCOME};')

        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setTitle('Анализ расходов')

        self.chartView = QChartView(self.chart)
        self.vboxChart.addWidget(self.chartView)

        self.spinBoxYear.setValue(dt.datetime.now().date().year)
        self.comboBoxMonth.setCurrentIndex(dt.datetime.now().date().month - 1)

    # Обработчик сигналов
    def initSignals(self):
        self.comboBoxMonth.currentIndexChanged.connect(self.currentDateOnChange)
        self.spinBoxYear.valueChanged.connect(self.changeCurrentDate)

        self.buttonAddExpense.clicked.connect(self.addExpenseOnClick)
        self.buttonAddIncome.clicked.connect(self.addIncomeOnClick)
        self.buttomAbout.clicked.connect(self.aboutProgram)

    # Событие при закрытии окна
    def closeEvent(self, *args, **kwargs):
        self.db.close()

    # Обработчик кнопки о программе
    def aboutProgram(self):
        DAbout().exec_()

    # Событие при изменении даты
    def currentDateOnChange(self, index):
        self.changeCurrentDate()

    def changeCurrentDate(self, update_last_date=True):
        if update_last_date:
            self.lastdate = QtCore.QDate(dt.date(self.spinBoxYear.value(), self.comboBoxMonth.currentIndex() + 1, 1))

        self.fillTable()
        self.fillSumms()
        self.fillChart()

    # Заполнение таблицы
    def fillTable(self):
        id = self.lastdate.toString('yyyyMM')

        sql = f"""SELECT strftime('%d.%m.%Y', date) as date, name, expense, income, comment
                           FROM transactions
                                LEFT JOIN
                                categories ON transactions.id_category = categories.id
                          WHERE strftime('%Y%m', date) = '{id}'
                          ORDER BY transactions.date DESC;"""

        model = QSqlQueryModel(self)
        model.setQuery(sql, db=self.db)

        model.setHeaderData(0, QtCore.Qt.Horizontal, 'Дата')
        model.setHeaderData(1, QtCore.Qt.Horizontal, 'Категория')
        model.setHeaderData(2, QtCore.Qt.Horizontal, 'Расход')
        model.setHeaderData(3, QtCore.Qt.Horizontal, 'Доход')
        model.setHeaderData(4, QtCore.Qt.Horizontal, 'Комментарий')

        self.tableView.setModel(model)
        self.tableView.setColumnWidth(0, 90)
        self.tableView.setColumnWidth(4, 200)
        self.tableView.setFocus()

    # Заполнение панели с суммами
    def fillSumms(self):
        self.sum_expense = 0.00
        self.sum_income = 0.00

        id = self.lastdate.toString('yyyyMM')
        sql = f"""SELECT SUM(expense) AS sum_expense, SUM(income) AS sum_income 
                    FROM transactions WHERE strftime('%Y%m', date) = '{id}'"""

        query = QSqlQuery()
        query.exec(sql)

        if query.isActive():
            query.first()

            if query.isValid():
                if not query.isNull('sum_expense'):
                    self.sum_expense = query.value('sum_expense')
                else:
                    self.sum_expense = 0.00

                if not query.isNull('sum_income'):
                    self.sum_income = query.value('sum_income')
                else:
                    self.sum_income = 0.00

        self.sum_balance = self.sum_income - self.sum_expense

        self.editExpense.setText(setRUBFormat(self.sum_expense))
        self.editIncome.setText(setRUBFormat(self.sum_income))
        self.editBalance.setText(setRUBFormat(self.sum_balance))

        if self.sum_balance < 0:
            self.editBalance.setStyleSheet(f'color: {COLOR_EXPENSE};')
        else:
            self.editBalance.setStyleSheet(f'color: {COLOR_INCOME};')

    # Заполнение диаграммы
    def fillChart(self):
        id = self.lastdate.toString('yyyyMM')
        sql = f"""SELECT name, SUM(expense) as sum_expense
                    FROM transactions
                    LEFT JOIN categories 
                        ON transactions.id_category = categories.id
                    WHERE categories.type = 1 AND strftime('%Y%m', date) = '{id}'
                    GROUP BY categories.id"""

        query = QSqlQuery()
        query.exec(sql)

        series = QPieSeries()
        series.setHoleSize(0.20)

        if query.isActive():
            query.first()

            while query.isValid():
                if not query.isNull('sum_expense'):
                    my_slice = series.append(query.value('name'), query.value('sum_expense'))
                    my_slice.setLabelVisible(True)

                query.next()

        self.chart.removeAllSeries()
        self.chart.addSeries(series)

    # Открытие диалогового окна расходы
    def addExpenseOnClick(self):
        dialog = Expense.DExpense(self.db, isincome=False)
        dialog.setDate(self.lastdate)
        result = dialog.exec_()

        if result == QtWidgets.QDialog.Accepted:
            self.lastdate = dialog.dateEdit.date()
            self.changeCurrentDate(update_last_date=False)

    # Открытие диалогового окна дохода
    def addIncomeOnClick(self):
        dialog = Expense.DExpense(self.db, isincome=True)
        dialog.setDate(self.lastdate)
        result = dialog.exec_()

        if result == QtWidgets.QDialog.Accepted:
            self.lastdate = dialog.dateEdit.date()
            self.changeCurrentDate(update_last_date=False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = CtrlMoney()
    main_window.show()
    main_window.changeCurrentDate()
    sys.exit(app.exec_())
