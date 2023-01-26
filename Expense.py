import datetime as dt

from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtSql import QSqlDatabase, QSqlQuery

COLOR_INCOME = '#00B050'
COLOR_EXPENSE = '#FF0000'
CHAR_RUBLE = ' ₽'


# Функция преобразования денежного формата
def setRUBFormat(value):
    return '{:,.2f}'.format(value).replace(',', ' ').replace('.', ',') + CHAR_RUBLE


# Класс окон расход/доход
class DExpense(QDialog):
    def __init__(self, db, isincome=False):
        super().__init__()
        self.db = db
        self.isincome = isincome
        self.categories = {}

        self.initUI()

        self.fillComboBox()

        self.initSignals()
        self.dateEdit.setFocus()

    # Инициализация интерфейса
    def initUI(self):
        uic.loadUi('forms/DExpense.ui', self)

        if self.isincome:
            self.setWindowTitle('Ввод дохода:')
            self.spinBoxSumma.setStyleSheet(f'color: {COLOR_INCOME};')
        else:
            self.setWindowTitle('Ввод расхода:')
            self.spinBoxSumma.setStyleSheet(f'color: {COLOR_EXPENSE};')

        self.spinBoxSumma.setSuffix(CHAR_RUBLE)

        self.btnOk = self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        self.btnOk.setEnabled(False)

        self.dateEdit.setDate(dt.datetime.now().date())
        self.comboBoxType.clear()

    # Обработчик сигналов
    def initSignals(self):
        self.spinBoxSumma.valueChanged.connect(self.summaOnChange)
        self.accepted.connect(self.onAccept)

    # Установка текущей даты
    def setDate(self, curdate):
        self.dateEdit.setDate(curdate)

    # Событие при изменении поля суммы
    def summaOnChange(self, value):
        if value > 0:
            self.btnOk.setEnabled(True)
        else:
            self.btnOk.setEnabled(False)

    # Заполнение выподающего списка категории
    def fillComboBox(self):
        id = 2 if self.isincome else 1
        sql = f"""SELECT id, name FROM categories WHERE type={id}"""

        query = QSqlQuery()
        query.exec(sql)

        if query.isActive():
            query.first()
            while query.isValid():
                cat_name = query.value('name')
                self.categories[cat_name] = query.value('id')
                self.comboBoxType.addItem(cat_name)
                query.next()

    # Запрос на добавление записи в базу данных
    def onAccept(self):
        curdate = self.dateEdit.date().toString('yyyy-MM-dd')
        id_category = self.categories[self.comboBoxType.currentText()]
        summa = self.spinBoxSumma.value()
        comment = self.lineEditComment.text()

        if self.isincome:
            sql = f"""INSERT INTO transactions(id_category, date, expense, income, comment) 
                      VALUES({id_category}, '{curdate}', 0.00, {summa:0.2f}, '{comment}')"""
        else:
            sql = f"""INSERT INTO transactions(id_category, date, expense, income, comment) 
                      VALUES({id_category}, '{curdate}', {summa:0.2f}, 0.00, '{comment}')"""

        query = QSqlQuery()
        query.exec(sql)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('db/test.db')
    db.open()

    dialog = DExpense(db)
    result = dialog.exec_()

    db.close()
