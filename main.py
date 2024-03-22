from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivy.core.audio import SoundLoader
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.tab import MDTabsBase
import sqlite3
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivymd.uix.list import ThreeLineAvatarIconListItem, IconRightWidget, OneLineAvatarIconListItem
import datetime, random
from kivymd.toast import toast
from kivy.uix.scrollview import ScrollView



class Show_all_borrowed_books(ScrollView):
    def __init__(self, result, **kwargs):
        super().__init__(**kwargs)
        self.title = result[1]
        self.id = result[0]


class User_edit_form(ScrollView):
    def __init__(self, id, **kwargs):
        super().__init__(**kwargs)
        self.id = id


class Book_edit_form(ScrollView):
    def __init__(self, id, **kwargs):
        super().__init__(**kwargs)
        self.id = id

    def category_suggestion(self, obj):
        i = 0
        items = list()
        self.suggest_category.dismiss()
        category = self.ids.add_book_category.text.strip()
        sql = f"""
            SELECT DISTINCT category FROM book
            WHERE category LIKE "{category}%"
        """
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        c.execute(sql)
        while result := c.fetchone():
            if i == 3:
                break
            items.append(
                {
                    "viewclass": "OneLineListItem",
                    "height": dp(56),
                    "text": f"{result[0]}",
                    "on_release": lambda x=result: self.set_category_values(x)
                })
            i += 1
        if items:
            self.suggest_category.items = items
            self.suggest_category.caller = obj
            self.suggest_category.width_mult = 5
            self.suggest_category.position = 'top'
            self.suggest_category.open()
        else:
            self.suggest_category.dismiss()
        conn.close()


class Tab(MDFloatLayout, MDTabsBase):
    pass


class PasswordTextField(MDRelativeLayout):
    hint_text = StringProperty()
    text = StringProperty()

    def clear(self):
        self.ids.password.text = ""

    def show_password(self):
        passw = self.ids.password
        if passw.password:
            passw.password = 0
            self.ids.eye_off.icon = 'eye'
        else:
            passw.password = 1
            self.ids.eye_off.icon = 'eye-off'

    def get_pass(self):
        return self.ids.password.text


class UserScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.suggest_book = MDDropdownMenu()
        self.show_detail = MDDialog()

    def get_loginer(self):
        global loginer
        info = f"""
            SELECT * FROM user WHERE user_id='{loginer[0]}'
        """
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        c.execute(info)
        result = c.fetchone()
        conn.close()
        return result

    def on_enter(self):
        result = self.get_loginer()
        self.ids.nav_drawer.set_state('open')
        snack = Snackbar(text=f"Welcome Dear {result[1]}!!!",
                         snackbar_x='30dp',
                         snackbar_y='30dp',
                         radius=[10, 10, 10, 10],
                         size_hint_x=0.5,
                         pos_hint={'center_x': 0.5},
                         duration=5
                         )
        snack.buttons = [
            MDFlatButton(text='DISMISS', on_release=snack.dismiss, theme_text_color="Custom", text_color="orange")]
        snack.open()

    def edit_user(self):
        id = self.user_id
        new_name = self.ids.edit_user_name.text
        new_phone_number = self.ids.edit_phone_number.text
        new_address = self.ids.edit_user_address.text
        new_fine = self.ids.edit_user_fine.text
        new_password = self.ids.edit_user_password.text
        if new_name:
            sql = f"""
                UPDATE user SET
                name='{new_name}'
                WHERE user_id='{id}'
            """
        if new_phone_number:
            sql = f"""
                UPDATE user SET
                phone_no='{new_phone_number}'
                WHERE user_id='{id}'
            """
        if new_address:
            sql = f"""
                UPDATE user SET
                address='{new_address}'
                WHERE user_id='{id}'
            """
        if new_fine:
            sql = f"""
                UPDATE user SET
                fine='{new_fine}'
                WHERE user_id='{id}'
            """
        if new_password:
            sql = f"""
                UPDATE user SET
                password='{new_password}'
                WHERE user_id='{id}'
            """
        if not new_name and not new_fine and not new_address and not new_password and not new_phone_number:
            toast("NO CHANGE")
            return

        conn = sqlite3.connect("library.db")
        c = conn.cursor()
        try:
            c.execute(sql)
        except Exception as e:
            toast("Something went wrong")
            print(e)
        else:
            conn.commit()
            new_address = ""
            new_fine = ""
            new_name = ""
            new_password = ""
            new_phone_number = ""
            toast("SUCCESSFUL")
        conn.close()

    def book_suggestion(self, obj):
        items = list()
        title = self.ids.search_book_by_title.text.strip()
        id = self.ids.search_book_by_id.text.strip()
        conn = sqlite3.connect("library.db")
        c = conn.cursor()
        if title or id:
            sql = f"""
                SELECT * FROM book
                WHERE 
                book_id LIKE "{id}%" AND
                title LIKE "{title}%" 
            """
        else:
            return
        c.execute(sql)
        i = 0
        while 1:
            result = c.fetchone()
            if result is None or i == 3:
                break
            items.append(
                {
                    "viewclass": "OneLineListItem",
                    "height": dp(56),
                    "text": f"TITLE: {result[1]} -- ID: {result[0]}",
                    "on_release": lambda x=result: self.set_book_values(x)
                })
            i += 1
        if items:
            self.suggest_book.items = items
            self.suggest_book.caller = obj
            self.suggest_book.width_mult = 5
            self.suggest_book.position = 'top'
            self.suggest_book.open()
        else:
            self.suggest_book.dismiss()
        conn.close()

    def set_book_values(self, result):
        result_list = self.ids.result_search_book
        result_list.clear_widgets()
        self.ids.search_book_by_title.text = str(result[1])
        self.ids.search_book_by_id.text = str(result[0])
        func = lambda x, y=result: self.show_book_detail(y)
        record = ThreeLineAvatarIconListItem(
            IconRightWidget(
                icon="book"
            ),
            text=f"ID: {result[0]} --- TITLE: {result[1]}",
            secondary_text=f"AUTHOR: {result[3]}",
            tertiary_text=f"Tap to view detail",
            on_release=func
        )
        result_list.add_widget(record)
        self.suggest_book.dismiss()

    def borrow_book(self):
        result_list = self.ids.list_borrowed_book_user
        user_id = self.get_loginer()[0]
        sql = f"""
            SELECT * FROM borrow_book
            WHERE user_id='{user_id}'
        """
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        c.execute(sql)
        results = c.fetchall()
        for result in results:
            sql_2 = f"""
                SELECT * FROM book
                WHERE book_id="{result[0]}"
            """
            c.execute(sql_2)
            book_info = c.fetchone()
            result_list.add_widget(
                ThreeLineAvatarIconListItem(
                    IconRightWidget(
                        icon="book"
                    ),
                    text=f"ID: {book_info[0]} --- TITLE: {book_info[1]}",
                    secondary_text=f"PUBLISHER: {book_info[2]} -- AUTHOR: {book_info[3]}",
                    tertiary_text=f"CATEGORY: {book_info[4]} -- PRICE: {book_info[5]}",
                    on_release=lambda x, y=book_info: self.show_book_detail(y)
                )
            )

    def show_book_detail(self, result):
        if not self.show_detail._is_open:
            self.show_detail = MDDialog(
                title='BOOK INFO',
                text=f"""
                TITLE: {result[1]}
                ID: {result[0]}
                PUBLISHER: {result[2]}
                AUTHOR: {result[3]}
                CATEGORY: {result[4]}
                PRICE: {result[5]}
            """,
                buttons=[
                    MDRaisedButton(text='OK', on_release=lambda x: self.show_detail.dismiss()),
                ]
            )
            self.show_detail.open()
        else:
            self.show_detail.dismiss()


class EmployeeScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.suggest_user = MDDropdownMenu()
        self.suggest_book = MDDropdownMenu()
        self.suggest_category = MDDropdownMenu()
        self.show_detail = MDDialog()

    def get_loginer(self):
        global loginer
        info = f"""
         SELECT * FROM staff WHERE staff_id='{loginer[0]}'
         """
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        c.execute(info)
        result = c.fetchone()
        conn.close()
        return result

    def on_enter(self):
        self.ids.nav_drawer.set_state('open')
        result = self.get_loginer()
        snack = Snackbar(text=f"Welcome dear {result[1]}!!!",
                         snackbar_x='30dp',
                         snackbar_y='30dp',
                         radius=[10, 10, 10, 10],
                         size_hint_x=0.5,
                         pos_hint={'center_x': 0.5},
                         duration=5
                         )
        snack.buttons = [
            MDFlatButton(text='DISMISS', on_release=snack.dismiss, theme_text_color="Custom", text_color="orange")]
        snack.open()

    def search_user(self):
        current_screen = self.ids.screenmanager_employee.current
        if current_screen == "search-user-admin":
            result_list = self.ids.result_search_user
            result_list.clear_widgets()
            name = self.ids.search_by_name.text.strip()
            id = self.ids.search_by_id.text.strip()
        elif current_screen == 'remove-user-admin':
            result_list = self.ids.result_remove_search_user
            result_list.clear_widgets()
            name = self.ids.remove_by_name.text.strip()
            id = self.ids.remove_by_id.text.strip()
        elif current_screen == 'edit-user-admin':
            result_list = self.ids.result_search_edit_user
            result_list.clear_widgets()
            name = self.ids.find_user_by_name.text.strip()
            id = self.ids.find_user_by_id.text.strip()

        conn = sqlite3.connect("library.db")
        c = conn.cursor()
        if name or id:
            sql = f"""
                SELECT * FROM user
                WHERE 
                user_id LIKE "{id}%" AND
                name LIKE "{name}%" 
            """
        else:
            return
        c.execute(sql)
        while 1:
            result = c.fetchone()
            if result is None:
                break
            if current_screen == "search-user-admin":
                func = lambda x, y=result: self.set_user_values(y)
                text = "Tap to view detail"
            elif current_screen == 'remove-user-admin':
                func = lambda x, y=result: self.remove_user(y)
                text = "Tap to remove"
            elif current_screen == 'edit-user-admin':
                func = lambda x, y=result: self.show_user_edit_dialog(y)
                text = "Tap to edit"
            result_list.add_widget(
                ThreeLineAvatarIconListItem(
                    IconRightWidget(
                        icon="account"
                    ),
                    text=f"ID: {result[0]} --- NAME: {result[1]}",
                    secondary_text=f"EXPIRE_DATE: {result[6]}",
                    tertiary_text=text,
                    on_release=func
                )
            )
        conn.close()

    def show_user_detail(self, result):
        if not self.show_detail._is_open:
            self.show_detail = MDDialog(
                title='USER INFO',
                text=f"""
                NAME: {result[1]}
                ID: {result[0]}
                ADDRESS: {result[2]}
                PHONE NUMBER: {result[4]}
                FINE: {result[5]}
                EXPIRE_DATE: {result[6]}
            """,
                buttons=[MDRaisedButton(text='OK', on_release=lambda x: self.show_detail.dismiss())]
            )
            self.show_detail.open()
        else:
            self.show_detail.dismiss()

    def user_suggestion(self, obj):
        items = list()
        self.suggest_user.dismiss()
        current_screen = self.ids.screenmanager_employee.current
        if current_screen == 'search-user-employee':
            name = self.ids.search_by_name.text.strip()
            id = self.ids.search_by_id.text.strip()
        elif current_screen == "borrowed-book-employee":
            id = self.ids.search_by_user_id.text.strip()
            name = self.ids.search_by_user_name.text.strip()
        conn = sqlite3.connect("library.db")
        c = conn.cursor()
        if name or id:
            sql = f"""
                SELECT * FROM user
                WHERE 
                user_id LIKE "{id}%" AND
                name LIKE "{name}%" 
            """
        else:
            return
        c.execute(sql)
        i = 0
        while 1:
            result = c.fetchone()
            if result is None or i == 3:
                break
            items.append(
                {
                    "viewclass": "OneLineListItem",
                    "height": dp(56),
                    "text": f"NAME: {result[1]} -- ID: {result[0]}",
                    "on_release": lambda x=result: self.set_user_values(x)
                })
            i += 1
        if items:
            self.suggest_user.items = items
            self.suggest_user.caller = obj
            self.suggest_user.width_mult = 5
            self.suggest_user.position = 'top'
            self.suggest_user.open()
        else:
            self.suggest_user.dismiss()
        conn.close()

    def show_user_detail(self, result):
        if not self.show_detail._is_open:
            self.show_detail = MDDialog(
                title='USER INFO',
                text=f"""
                NAME: {result[1]}
                ID: {result[0]}
                ADDRESS: {result[2]}
                PHONE NUMBER: {result[4]}
                FINE: {result[5]}
                EXPIRE_DATE: {result[6]}
            """,
                buttons=[MDRaisedButton(text='OK', on_release=lambda x: self.show_detail.dismiss())]
            )
            self.show_detail.open()
        else:
            self.show_detail.dismiss()

    def set_user_values(self, result):
        current_screen = self.ids.screenmanager_employee.current
        self.suggest_user.dismiss()
        if current_screen == "search-user-employee":
            result_list = self.ids.result_search_user
            result_list.clear_widgets()
            self.ids.search_by_name.text = str(result[1])
            self.ids.search_by_id.text = str(result[0])
            func = lambda x, y=result: self.show_user_detail(y)
            record = ThreeLineAvatarIconListItem(
                IconRightWidget(
                    icon="account"
                ),
                text=f"ID: {result[0]} --- NAME: {result[1]}",
                secondary_text=f"EXPIRE_DATE: {result[6]}",
                tertiary_text=f"Tap to view detail",
                on_release=func
            )
            result_list.add_widget(record)
        elif current_screen == "borrowed-book-employee":
            result_list = self.ids.result_borrowed_book
            result_list.clear_widgets()
            self.ids.search_by_user_id.text = str(result[0])
            self.ids.search_by_user_name.text = str(result[1])
            conn = sqlite3.connect('library.db')
            c = conn.cursor()
            sql_1 = f"""
                SELECT * FROM borrow_book
                WHERE user_id='{result[0]}'
            """
            c.execute(sql_1)
            books = c.fetchmany()
            for book in books:
                sql_2 = f"""
                    SELECT title FROM book
                    WHERE book_id="{book[0]}"
                """
                c.execute(sql_2)
                book_title = c.fetchone()[0]
                record = ThreeLineAvatarIconListItem(
                    IconRightWidget(
                        icon="book"
                    ),
                    text=f"ID: {book[0]} --- TITLE: {book_title}",
                    secondary_text=f"EXPIRE_DATE: {book[3]}",
                    tertiary_text=f"BORROW_DATE: {book[2]}",
                    on_release=lambda x, y=result[0], z=book[0]: self.get_book_back(y, z)
                )
                result_list.add_widget(record)
            conn.close()

    def get_book_back(self, user_id, book_id):
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        sql = f"""
            DELETE FROM borrow_book
            WHERE 
            user_id="{user_id}" AND
            book_id="{book_id}"
        """
        try:
            c.execute(sql)
        except Exception as e:
            toast("something went wrong :(")
            print(e)
        else:
            conn.commit()
            self.ids.search_by_book_id.text = ""
            self.ids.search_by_book_title.text = ""
            self.ids.search_by_user_id.text = ""
            self.ids.search_by_user_name.text = ""
            self.ids.result_borrowed_book.clear_widgets()
            toast("Get Back Successful !")

        conn.close()

    def book_suggestion(self, obj):
        items = list()
        self.suggest_book.dismiss()
        current_screen = self.ids.screenmanager_employee.current
        if current_screen == "borrowed-book-employee":
            id = self.ids.search_by_book_id.text.strip()
            title = self.ids.search_by_book_title.text.strip()
        elif current_screen == "search-book-employee":
            title = self.ids.search_book_by_title.text.strip()
            id = self.ids.search_book_by_id.text.strip()

        conn = sqlite3.connect("library.db")
        c = conn.cursor()
        if title or id:
            sql = f"""
                SELECT * FROM book
                WHERE 
                book_id LIKE "{id}%" AND
                title LIKE "{title}%" 
            """
        else:
            return
        c.execute(sql)
        i = 0
        while 1:
            result = c.fetchone()
            if result is None or i == 3:
                break
            items.append(
                {
                    "viewclass": "OneLineListItem",
                    "height": dp(56),
                    "text": f"TITLE: {result[1]} -- ID: {result[0]}",
                    "on_release": lambda x=result: self.set_book_values(x)
                })
            i += 1
        if items:
            self.suggest_book.items = items
            self.suggest_book.caller = obj
            self.suggest_book.width_mult = 5
            self.suggest_book.position = 'top'
            self.suggest_book.open()
        else:
            self.suggest_book.dismiss()
        conn.close()

    def set_book_values(self, result):
        current_screen = self.ids.screenmanager_employee.current
        if current_screen == "borrowed-book-employee":
            result_list = self.ids.result_borrowed_book
            result_list.clear_widgets()
            self.ids.search_by_book_id.text = str(result[0])
            self.ids.search_by_book_title.text = str(result[1])
            conn = sqlite3.connect("library.db")
            c = conn.cursor()
            sql_1 = f"""
                SELECT user_id FROM borrow_book
                WHERE book_id = "{result[0]}"
            
            """
            c.execute(sql_1)
            user_id = c.fetchone()
            if user_id:
                sql_2 = f"""
                    SELECT * FROM user
                    WHERE user_id="{user_id[0]}"
                """
                c.execute(sql_2)
                user_info = c.fetchone()
                record = ThreeLineAvatarIconListItem(
                    IconRightWidget(
                        icon="account"
                    ),
                    text=f"ID: {user_info[0]} --- NAME: {user_info[1]}",
                    secondary_text=f"ADDRESS: {user_info[2]}---PHONE: {user_info[4]}",
                    tertiary_text=f"Tap to Get Back",
                    on_release=lambda x, y=user_info[0], z=result[0]: self.get_book_back(y, z)
                )
                result_list.add_widget(record)
            conn.close()

        elif current_screen == "search-book-employee":
            result_list = self.ids.result_search_book
            result_list.clear_widgets()
            self.ids.search_book_by_title.text = str(result[1])
            self.ids.search_book_by_id.text = str(result[0])
            func = lambda x, y=result: self.show_book_detail(y)
            record = ThreeLineAvatarIconListItem(
                IconRightWidget(
                    icon="book"
                ),
                text=f"ID: {result[0]} --- TITLE: {result[1]}",
                secondary_text=f"AUTHOR: {result[3]}",
                tertiary_text=f"Tap to view detail",
                on_release=func
            )
            result_list.add_widget(record)

    def show_book_detail(self, result):
        if not self.show_detail._is_open:
            self.show_detail = MDDialog(
                title='BOOK INFO',
                text=f"""
                TITLE: {result[1]}
                ID: {result[0]}
                PUBLISHER: {result[2]}
                AUTHOR: {result[3]}
                CATEGORY: {result[4]}
                PRICE: {result[5]}
            """,
                buttons=[
                    MDRaisedButton(text='OK', on_release=lambda x: self.show_detail.dismiss()),
                ]
            )
            self.show_detail.open()
        else:
            self.show_detail.dismiss()

    def borrow_book(self):
        book_id = self.ids.search_by_book_id
        user_id = self.ids.search_by_user_id
        borrow_time = str(datetime.datetime.now()).split()[0]
        expire_time = str(datetime.datetime.now() + datetime.timedelta(days=60)).split()[0]
        inputs = [book_id, user_id]
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        if book_id.text and user_id.text:
            sql = f"""
                INSERT INTO borrow_book 
                (book_id, user_id, borrow_date, expire_date)
                VALUES
                ('{book_id.text}', '{user_id.text}', '{borrow_time}', '{expire_time}')
            """
            c.execute(sql)
            conn.commit()
            toast("SUCCESSFUL!")
            book_id.text = ""
            user_id.text = ""
            self.ids.search_by_book_title.text = ""
            self.ids.search_by_user_name.text = ""
        else:
            for i in inputs:
                if not i:
                    i.error = 1
        conn.close()

    def search_book(self):
        result_list = self.ids.result_search_book
        result_list.clear_widgets()
        title = self.ids.search_book_by_title.text.strip()
        id = self.ids.search_book_by_id.text.strip()

        conn = sqlite3.connect("library.db")
        c = conn.cursor()
        if title or id:
            sql = f"""
                SELECT * FROM book
                WHERE 
                book_id LIKE "{id}%" AND
                title LIKE "{title}%" 
            """
        else:
            return
        c.execute(sql)
        while 1:
            result = c.fetchone()
            if not result:
                break

            func = lambda y, x=result: self.show_book_detail(x)
            text = "Tap to view detail"

            result_list.add_widget(
                ThreeLineAvatarIconListItem(
                    IconRightWidget(
                        icon="book"
                    ),
                    text=f"ID: {result[0]} --- TITLE: {result[1]}",
                    secondary_text=f"AUTHOR: {result[3]}",
                    tertiary_text=text,
                    on_release=func
                )
            )

        conn.close()


class AdminScreen(MDScreen):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.suggest_user = MDDropdownMenu()
        self.suggest_book = MDDropdownMenu()
        self.suggest_category = MDDropdownMenu()
        self.show_detail = MDDialog()

    def get_loginer(self):
        global loginer
        info = f"""
        SELECT * FROM staff WHERE staff_id='{loginer[0]}'
        """
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        c.execute(info)
        result = c.fetchone()
        conn.close()
        return result

    def on_enter(self, *args):
        result = self.get_loginer()
        snack = Snackbar(text=f"Welcome dear {result[1]}!!!",
                         snackbar_x='30dp',
                         snackbar_y='30dp',
                         radius=[10, 10, 10, 10],
                         size_hint_x=0.5,
                         pos_hint={'center_x': 0.5},
                         duration=5
                         )
        snack.buttons = [
            MDFlatButton(text='DISMISS', on_release=snack.dismiss, theme_text_color="Custom", text_color="orange")]
        snack.open()
        self.ids.nav_drawer.set_state('open')

    def remove_book(self, book_id):
        sql = f"""
            DELETE FROM book 
            WHERE book_id="{book_id}"
        """
        conn = sqlite3.connect("library.db")
        c = conn.cursor()
        try:
            c.execute(sql)
        except Exception as e:
            toast('something went wrong!')
            print(e)
        else:
            conn.commit()
            toast('Remove book successfull!')
            self.ids.search_book_by_title.text = ""
            self.ids.search_book_by_id.text = ""
            self.ids.result_search_book.clear_widgets()
        finally:
            self.show_detail.dismiss()
            conn.close()

    def show_user_edit_dialog(self, id):
        edit_form = User_edit_form(id)
        if not self.show_detail._is_open:
            self.show_detail = MDDialog(
                title='EDIT USER INFO',
                type="custom",
                content_cls=edit_form,
                buttons=[
                    MDFlatButton(text='Dismiss', on_release=lambda x: self.show_detail.dismiss()),
                    MDRaisedButton(text='OK', on_release=lambda x: self.commit_user_edit(edit_form)),
                ]
            )
            self.show_detail.open()
        else:
            self.show_detail.dismiss()

    def commit_user_edit(self, obj):
        id = obj.id
        new_name = obj.ids.edit_user_name.text
        new_phone_number = obj.ids.edit_phone_number.text
        new_address = obj.ids.edit_user_address.text
        new_fine = obj.ids.edit_user_fine.text
        new_password = obj.ids.edit_user_password.text
        if new_name:
            sql = f"""
                UPDATE user SET
                name='{new_name}'
                WHERE user_id='{id}'
            """
        if new_phone_number:
            sql = f"""
                UPDATE user SET
                phone_no='{new_phone_number}'
                WHERE user_id='{id}'
            """
        if new_address:
            sql = f"""
                UPDATE user SET
                address='{new_address}'
                WHERE user_id='{id}'
            """
        if new_fine:
            sql = f"""
                UPDATE user SET
                fine='{new_fine}'
                WHERE user_id='{id}'
            """
        if new_password:
            sql = f"""
                UPDATE user SET
                password='{new_password}'
                WHERE user_id='{id}'
            """
        if not new_name and not new_fine and not new_address and not new_password and not new_phone_number:
            self.show_detail.dismiss()
            toast("NO CHANGE")
            return

        conn = sqlite3.connect("library.db")
        c = conn.cursor()
        try:
            c.execute(sql)
        except Exception as e:
            toast("Something went wrong")
            print(e)
        else:
            conn.commit()
            self.show_detail.dismiss()
            self.ids.find_user_by_name.text = ""
            self.ids.find_user_by_id.text = ""
            self.ids.result_search_edit_user.clear_widgets()
            toast("SUCCESSFUL")
        conn.close()

    def add_user(self):
        num_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        id = "".join(random.choices(num_list, k=5))
        name = self.ids.add_user_name
        address = self.ids.add_user_address
        phone_number = self.ids.add_user_phone
        password = "".join(random.choices(num_list, k=5))
        fine = 0
        expire_date = datetime.datetime.now() + datetime.timedelta(days=365)

        inputs = [name, address, phone_number]
        for i in inputs:
            i.error = 0

        if name.text and address.text and phone_number.text:
            sql = f"""
                INSERT INTO user 
                (user_id, name, address, phone_no, password, fine, expire_date)
                VALUES
                ('{id}', '{str(name.text.strip())}', '{str(address.text.strip())}', '{phone_number.text.strip()}', '{str(password)}', '{fine}', '{str(expire_date).split()[0]}')
            """
        else:
            for i in inputs:
                if not i.text:
                    i.error = 1
            return

        conn = sqlite3.connect("library.db")
        c = conn.cursor()
        try:
            c.execute(sql)
        except sqlite3.IntegrityError:
            toast("Phone number Already exists!")
        except Exception as e:
            toast('Something went wrong')
            print(e)
        else:
            conn.commit()
            toast("User Added Successfully !")
            name.text = ""
            address.text = ""
            phone_number.text = ""
        conn.close()

    def search_user(self):
        current_screen = self.ids.screenmanager_admin.current
        if current_screen == "search-user-admin":
            result_list = self.ids.result_search_user
            result_list.clear_widgets()
            name = self.ids.search_by_name.text.strip()
            id = self.ids.search_by_id.text.strip()
        elif current_screen == 'remove-user-admin':
            result_list = self.ids.result_remove_search_user
            result_list.clear_widgets()
            name = self.ids.remove_by_name.text.strip()
            id = self.ids.remove_by_id.text.strip()
        elif current_screen == 'edit-user-admin':
            result_list = self.ids.result_search_edit_user
            result_list.clear_widgets()
            name = self.ids.find_user_by_name.text.strip()
            id = self.ids.find_user_by_id.text.strip()

        conn = sqlite3.connect("library.db")
        c = conn.cursor()
        if name or id:
            sql = f"""
                SELECT * FROM user
                WHERE 
                user_id LIKE "{id}%" AND
                name LIKE "{name}%" 
            """
        else:
            return
        c.execute(sql)
        while 1:
            result = c.fetchone()
            if result is None:
                break
            if current_screen == "search-user-admin":
                func = lambda x, y=result: self.set_user_values(y)
                text = "Tap to view detail"
            elif current_screen == 'remove-user-admin':
                func = lambda x, y=result: self.remove_user(y)
                text = "Tap to remove"
            elif current_screen == 'edit-user-admin':
                func = lambda x, y=result: self.show_user_edit_dialog(y)
                text = "Tap to edit"
            result_list.add_widget(
                ThreeLineAvatarIconListItem(
                    IconRightWidget(
                        icon="account"
                    ),
                    text=f"ID: {result[0]} --- NAME: {result[1]}",
                    secondary_text=f"EXPIRE_DATE: {result[6]}",
                    tertiary_text=text,
                    on_release=func
                )
            )
        conn.close()

    def show_user_detail(self, result):
        if not self.show_detail._is_open:
            self.show_detail = MDDialog(
                title='USER INFO',
                text=f"""
                NAME: {result[1]}
                ID: {result[0]}
                ADDRESS: {result[2]}
                PHONE NUMBER: {result[4]}
                FINE: {result[5]}
                EXPIRE_DATE: {result[6]}
            """,
                buttons=[MDRaisedButton(text='OK', on_release=lambda x: self.show_detail.dismiss())]
            )
            self.show_detail.open()
        else:
            self.show_detail.dismiss()

    def user_suggestion(self, obj):
        items = list()
        self.suggest_user.dismiss()
        current_screen = self.ids.screenmanager_admin.current
        if current_screen == "search-user-admin":
            name = self.ids.search_by_name.text.strip()
            id = self.ids.search_by_id.text.strip()
        elif current_screen == "edit-user-admin":
            name = self.ids.find_user_by_name.text.strip()
            id = self.ids.find_user_by_id.text.strip()
        elif current_screen == 'remove-user-admin':
            name = self.ids.remove_by_name.text.strip()
            id = self.ids.remove_by_id.text.strip()
        elif current_screen == "borrowed-book-admin":
            id = self.ids.search_by_user_id.text.strip()
            name = self.ids.search_by_user_name.text.strip()

        conn = sqlite3.connect("library.db")
        c = conn.cursor()
        if name or id:
            sql = f"""
                SELECT * FROM user
                WHERE 
                user_id LIKE "{id}%" AND
                name LIKE "{name}%" 
            """
        else:
            return
        c.execute(sql)
        i = 0
        while 1:
            result = c.fetchone()
            if result is None or i == 3:
                break
            items.append(
                {
                    "viewclass": "OneLineListItem",
                    "height": dp(56),
                    "text": f"NAME: {result[1]} -- ID: {result[0]}",
                    "on_release": lambda x=result: self.set_user_values(x)
                })
            i += 1
        if items:
            self.suggest_user.items = items
            self.suggest_user.caller = obj
            self.suggest_user.width_mult = 5
            self.suggest_user.position = 'top'
            self.suggest_user.open()
        else:
            self.suggest_user.dismiss()
        conn.close()

    def set_user_values(self, result):
        current_screen = self.ids.screenmanager_admin.current
        self.suggest_user.dismiss()
        if current_screen == "search-user-admin":
            result_list = self.ids.result_search_user
            result_list.clear_widgets()
            self.ids.search_by_name.text = str(result[1])
            self.ids.search_by_id.text = str(result[0])
            func = lambda x, y=result: self.show_user_detail(y)
            record = ThreeLineAvatarIconListItem(
                IconRightWidget(
                    icon="account"
                ),
                text=f"ID: {result[0]} --- NAME: {result[1]}",
                secondary_text=f"EXPIRE_DATE: {result[6]}",
                tertiary_text=f"Tap to view detail",
                on_release=func
            )
            result_list.add_widget(record)
        elif current_screen == "edit-user-admin":
            result_list = self.ids.result_search_edit_user
            result_list.clear_widgets()
            self.ids.find_user_by_name.text = str(result[1])
            self.ids.find_user_by_id.text = str(result[0])
            func = lambda x, y=result[0]: self.show_user_edit_dialog(y)
            record = ThreeLineAvatarIconListItem(
                IconRightWidget(
                    icon="account"
                ),
                text=f"ID: {result[0]} --- NAME: {result[1]}",
                secondary_text=f"EXPIRE_DATE: {result[6]}",
                tertiary_text=f"Tap to Edit",
                on_release=func
            )
            result_list.add_widget(record)
        elif current_screen == 'remove-user-admin':
            result_list = self.ids.result_remove_search_user
            result_list.clear_widgets()
            self.ids.remove_by_name.text = str(result[1])
            self.ids.remove_by_id.text = str(result[0])
            func = lambda x, y=[result[0], result[1]]: self.remove_user(y)
            record = ThreeLineAvatarIconListItem(
                IconRightWidget(
                    icon="account"
                ),
                text=f"ID: {result[0]} --- NAME: {result[1]}",
                secondary_text=f"EXPIRE_DATE: {result[6]}",
                tertiary_text=f"Tap to remove",
                on_release=func
            )
            result_list.add_widget(record)
        elif current_screen == "borrowed-book-admin":
            result_list = self.ids.result_borrowed_book
            result_list.clear_widgets()
            self.ids.search_by_user_id.text = str(result[0])
            self.ids.search_by_user_name.text = str(result[1])
            conn = sqlite3.connect('library.db')
            c = conn.cursor()
            sql_1 = f"""
                SELECT * FROM borrow_book
                WHERE user_id='{result[0]}'
            """
            c.execute(sql_1)
            books = c.fetchmany()
            for book in books:
                sql_2 = f"""
                    SELECT title FROM book
                    WHERE book_id="{book[0]}"
                """
                c.execute(sql_2)
                book_title = c.fetchone()[0]
                record = ThreeLineAvatarIconListItem(
                    IconRightWidget(
                        icon="book"
                    ),
                    text=f"ID: {book[0]} --- TITLE: {book_title}",
                    secondary_text=f"EXPIRE_DATE: {book[3]}",
                    tertiary_text=f"BORROW_DATE: {book[2]}",
                    on_release=lambda x, y=result[0], z=book[0]: self.get_book_back(y, z)
                )
                result_list.add_widget(record)
            conn.close()

    def get_book_back(self, user_id, book_id):
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        sql = f"""
            DELETE FROM borrow_book
            WHERE 
            user_id="{user_id}" AND
            book_id="{book_id}"
        """
        try:
            c.execute(sql)
        except Exception as e:
            toast("something went wrong :(")
            print(e)
        else:
            conn.commit()
            self.ids.search_by_book_id.text = ""
            self.ids.search_by_book_title.text = ""
            self.ids.search_by_user_id.text = ""
            self.ids.search_by_user_name.text = ""
            self.ids.result_borrowed_book.clear_widgets()
            toast("Get Back Successful !")

        conn.close()

    def book_suggestion(self, obj):
        items = list()
        self.suggest_book.dismiss()
        current_screen = self.ids.screenmanager_admin.current
        if current_screen == "borrowed-book-admin":
            id = self.ids.search_by_book_id.text.strip()
            title = self.ids.search_by_book_title.text.strip()
        elif current_screen == "search-book-admin":
            title = self.ids.search_book_by_title.text.strip()
            id = self.ids.search_book_by_id.text.strip()
        elif current_screen == "edit-book-admin":
            title = self.ids.find_book_by_title.text.strip()
            id = self.ids.find_book_by_id.text.strip()
        conn = sqlite3.connect("library.db")
        c = conn.cursor()
        if title or id:
            sql = f"""
                SELECT * FROM book
                WHERE 
                book_id LIKE "{id}%" AND
                title LIKE "{title}%" 
            """
        else:
            return
        c.execute(sql)
        i = 0
        while 1:
            result = c.fetchone()
            if result is None or i == 3:
                break
            items.append(
                {
                    "viewclass": "OneLineListItem",
                    "height": dp(56),
                    "text": f"TITLE: {result[1]} -- ID: {result[0]}",
                    "on_release": lambda x=result: self.set_book_values(x)
                })
            i += 1
        if items:
            self.suggest_book.items = items
            self.suggest_book.caller = obj
            self.suggest_book.width_mult = 5
            self.suggest_book.position = 'top'
            self.suggest_book.open()
        else:
            self.suggest_book.dismiss()
        conn.close()

    def set_book_values(self, result):
        current_screen = self.ids.screenmanager_admin.current
        self.suggest_book.dismiss()
        if current_screen == "borrowed-book-admin":
            result_list = self.ids.result_borrowed_book
            result_list.clear_widgets()
            self.ids.search_by_book_id.text = str(result[0])
            self.ids.search_by_book_title.text = str(result[1])
            conn = sqlite3.connect("library.db")
            c = conn.cursor()
            sql_1 = f"""
                SELECT user_id FROM borrow_book
                WHERE book_id = "{result[0]}"
            
            """
            c.execute(sql_1)
            user_id = c.fetchone()
            if user_id:
                sql_2 = f"""
                    SELECT * FROM user
                    WHERE user_id="{user_id[0]}"
                """
                c.execute(sql_2)
                user_info = c.fetchone()
                record = ThreeLineAvatarIconListItem(
                    IconRightWidget(
                        icon="account"
                    ),
                    text=f"ID: {user_info[0]} --- NAME: {user_info[1]}",
                    secondary_text=f"ADDRESS: {user_info[2]}---PHONE: {user_info[4]}",
                    tertiary_text=f"Tap to Get Back",
                    on_release=lambda x, y=user_info[0], z=result[0]: self.get_book_back(y, z)
                )
                result_list.add_widget(record)
            conn.close()

        elif current_screen == "search-book-admin":
            result_list = self.ids.result_search_book
            result_list.clear_widgets()
            self.ids.search_book_by_title.text = str(result[1])
            self.ids.search_book_by_id.text = str(result[0])
            func = lambda x, y=result: self.show_book_detail(y)
            record = ThreeLineAvatarIconListItem(
                IconRightWidget(
                    icon="book"
                ),
                text=f"ID: {result[0]} --- TITLE: {result[1]}",
                secondary_text=f"AUTHOR: {result[3]}",
                tertiary_text=f"Tap to view detail",
                on_release=func
            )
            result_list.add_widget(record)

        elif current_screen == "edit-book-admin":
            result_list = self.ids.result_search_edit_user
            result_list.clear_widgets()
            self.ids.find_book_by_title.text = str(result[1])
            self.ids.find_book_by_id.text = str(result[0])
            func = lambda x, y=result[0]: self.show_book_edit_dialog(y)
            record = ThreeLineAvatarIconListItem(
                IconRightWidget(
                    icon="book"
                ),
                text=f"ID: {result[0]} --- TITLE: {result[1]}",
                secondary_text=f"AUTHOR: {result[2]}",
                tertiary_text=f"Tap to Edit",
                on_release=func
            )
            result_list.add_widget(record)

    def show_book_edit_dialog(self, id):
        edit_form = Book_edit_form(id)
        if not self.show_detail._is_open:
            self.show_detail = MDDialog(
                title='EDIT BOOK INFO',
                type="custom",
                content_cls=edit_form,
                buttons=[
                    MDFlatButton(text='Dismiss', on_release=lambda x: self.show_detail.dismiss()),
                    MDRaisedButton(text='OK', on_release=lambda x: self.commit_book_edit(edit_form)),
                ]
            )
            self.show_detail.open()
        else:
            self.show_detail.dismiss()

    def show_book_detail(self, result):
        if not self.show_detail._is_open:
            self.show_detail = MDDialog(
                title='BOOK INFO',
                text=f"""
                TITLE: {result[1]}
                ID: {result[0]}
                PUBLISHER: {result[2]}
                AUTHOR: {result[3]}
                CATEGORY: {result[4]}
                PRICE: {result[5]}
            """,
                buttons=[
                    MDRaisedButton(text='REMOVE', on_release=lambda y, x=result[0]: self.remove_book(x),
                                   md_bg_color=[1, 0, 0, 1]),
                    MDRaisedButton(text='OK', on_release=lambda x: self.show_detail.dismiss()),
                ]
            )
            self.show_detail.open()
        else:
            self.show_detail.dismiss()

    def remove_user(self, result):
        if not self.check_borrowed_book(result):
            if not self.show_detail._is_open:
                self.show_detail = MDDialog(
                    title='REMOVE USER ?',
                    text=f"""
                    NAME: {result[1]}
                    ID: {result[0]}
                    """,
                    buttons=[
                        MDRaisedButton(text='NO', on_release=lambda x: self.show_detail.dismiss()),
                        MDFlatButton(text='YES', on_release=lambda x: self.commit_remove(result[0])),
                    ]
                )
                self.show_detail.open()
            else:
                self.show_detail.dismiss()

    def commit_remove(self, id):
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        sql = f"""
            DELETE FROM user 
            WHERE user_id='{id}'
        """
        c.execute(sql)
        conn.commit()
        conn.close()
        self.show_detail.dismiss()
        self.ids.remove_by_name.text = ""
        self.ids.remove_by_id.text = ""
        self.ids.result_remove_search_user.clear_widgets()
        toast('Remove User Success!')

    def remove_user_error(self, user, books):
        show_all_borrowed_book = Show_all_borrowed_books(user)
        for book in books:
            show_all_borrowed_book.ids.result_list.add_widget(
                OneLineAvatarIconListItem(
                    text=f'ID: {book[1]} --- TITLE: {book[0]}'
                )
            )
        self.show_error = \
            MDDialog(
                type="custom",
                title=f'{user[1]} Already has some borrowed book',
                content_cls=show_all_borrowed_book,
                buttons=[
                    MDRaisedButton(text="OK", on_release=lambda x: self.show_error.dismiss())
                ]
            )
        self.show_error.open()

    def check_borrowed_book(self, user_info):
        item = list()
        sql = f"""
            SELECT * FROM borrow_book
            WHERE user_id="{user_info[0]}"
        """
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        c.execute(sql)
        while result := c.fetchone():
            sql_2 = f"""
                SELECT title, book_id FROM book
                WHERE book_id="{result[0]}"
            """
            c.execute(sql_2)
            item.append(c.fetchone())

        if item:
            conn.close()
            self.remove_user_error(user_info, item)
            return 1
        else:
            conn.close()
            return 0

    def borrow_book(self):
        book_id = self.ids.search_by_book_id
        user_id = self.ids.search_by_user_id
        borrow_time = str(datetime.datetime.now()).split()[0]
        expire_time = str(datetime.datetime.now() + datetime.timedelta(days=60)).split()[0]
        inputs = [book_id, user_id]
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        if book_id.text and user_id.text:
            sql = f"""
                INSERT INTO borrow_book 
                (book_id, user_id, borrow_date, expire_date)
                VALUES
                ('{book_id.text}', '{user_id.text}', '{borrow_time}', '{expire_time}')
            """
            c.execute(sql)
            conn.commit()
            toast("SUCCESSFUL!")
            book_id.text = ""
            user_id.text = ""
            self.ids.search_by_book_title.text = ""
            self.ids.search_by_user_name.text = ""
        else:
            for i in inputs:
                if not i:
                    i.error = 1
        conn.close()

    def search_book(self):
        current_screen = self.ids.screenmanager_admin.current
        if current_screen == "search-book-admin":
            result_list = self.ids.result_search_book
            result_list.clear_widgets()
            title = self.ids.search_book_by_title.text.strip()
            id = self.ids.search_book_by_id.text.strip()
        elif current_screen == "edit-book-admin":
            title = self.ids.find_book_by_title.text.strip()
            id = self.ids.find_book_by_id.text.strip()

        conn = sqlite3.connect("library.db")
        c = conn.cursor()
        if title or id:
            sql = f"""
                SELECT * FROM book
                WHERE 
                book_id LIKE "{id}%" AND
                title LIKE "{title}%" 
            """
        else:
            return
        c.execute(sql)
        while 1:
            result = c.fetchone()
            if not result:
                break
            if current_screen == "search-book-admin":
                func = lambda y, x=result: self.show_book_detail(x)
                text = "Tap to view detail"
            elif current_screen == "edit-book-admin":
                result_list = self.ids.result_search_edit_book
                result_list.clear_widgets()
                func = lambda x, y=result[0]: self.show_book_edit_dialog(y)
                text = 'Tap to edit book info'

            result_list.add_widget(
                ThreeLineAvatarIconListItem(
                    IconRightWidget(
                        icon="book"
                    ),
                    text=f"ID: {result[0]} --- TITLE: {result[1]}",
                    secondary_text=f"AUTHOR: {result[3]}",
                    tertiary_text=text,
                    on_release=func
                )
            )

        conn.close()

    def category_suggestion(self, obj):
        i = 0
        items = list()
        self.suggest_category.dismiss()
        category = self.ids.add_book_category.text.strip()
        sql = f"""
            SELECT DISTINCT category FROM book
            WHERE category LIKE "{category}%"
        """
        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        c.execute(sql)
        while result := c.fetchone():
            if i == 3:
                break
            items.append(
                {
                    "viewclass": "OneLineListItem",
                    "height": dp(56),
                    "text": f"{result[0]}",
                    "on_release": lambda x=result: self.set_category_values(x)
                })
            i += 1
        if items:
            self.suggest_category.items = items
            self.suggest_category.caller = obj
            self.suggest_category.width_mult = 5
            self.suggest_category.position = 'top'
            self.suggest_category.open()
        else:
            self.suggest_category.dismiss()
        conn.close()

    def set_category_values(self, value):
        self.ids.add_book_category.text = value[0]

    def add_book(self):
        num_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        id = "".join(random.choices(num_list, k=5))
        title = self.ids.add_book_title
        publisher = self.ids.add_book_pub
        author = self.ids.add_book_author
        category = self.ids.add_book_category
        price = self.ids.add_book_price

        inputs = [title, publisher, author, category, price]
        for i in inputs:
            i.error = 0

        if title.text and publisher.text and author.text and category.text and price.text:
            sql = f"""
                INSERT INTO book
                (book_id, title, author, category, publisher,price)
                VALUES
                ('{id}', '{str(title.text.strip())}', '{str(author.text.strip())}', '{category.text.strip()}', '{publisher.text.strip()}', '{price.text.strip()}')
            """
        else:
            for i in inputs:
                if not i.text:
                    i.error = 1
            return

        conn = sqlite3.connect("library.db")
        c = conn.cursor()
        try:
            c.execute(sql)
        except Exception as e:
            toast('Something went wrong')
            print(e)
        else:
            conn.commit()
            toast("Book Added Successfully !")
            title.text = ""
            publisher.text = ""
            author.text = ""
            category.text = ""
            price.text = ""
        conn.close()

    def commit_book_edit(self, obj):
        id = obj.id
        new_title = obj.ids.edit_book_title.text
        new_author = obj.ids.edit_book_author.text
        new_pub = obj.ids.edit_book_publisher.text
        new_price = obj.ids.edit_book_price.text
        new_category = obj.ids.edit_book_category.text
        if new_title:
            sql = f"""
                UPDATE book SET
                title='{new_title}'
                WHERE book_id='{id}'
            """
        if new_author:
            sql = f"""
                UPDATE book SET
                author='{new_author}'
                WHERE book_id='{id}'
            """
        if new_pub:
            sql = f"""
                UPDATE book SET
                publisher='{new_pub}'
                WHERE book_id='{id}'
            """
        if new_price:
            sql = f"""
                UPDATE book SET
                price='{new_price}'
                WHERE book_id='{id}'
            """
        if new_category:
            sql = f"""
                UPDATE book SET
                category='{new_category}'
                WHERE book_id='{id}'
            """
        if not new_title and not new_price and not new_pub and not new_author and not new_category:
            self.show_detail.dismiss()
            toast("NO CHANGE")
            return

        conn = sqlite3.connect("library.db")
        c = conn.cursor()
        try:
            c.execute(sql)
        except Exception as e:
            toast("Something went wrong")
            print(e)
        else:
            conn.commit()
            self.show_detail.dismiss()
            self.ids.find_book_by_title.text = ""
            self.ids.find_book_by_id.text = ""
            self.ids.result_search_edit_book.clear_widgets()
            toast("SUCCESSFUL")
        conn.close()


class LoginScreen(MDScreen):
    login_type = ""

    def on_enter(self):
        Clock.schedule_once(self.show_snackbar, 3)

    def show_snackbar(self, *args):
        self.snack = Snackbar(
            text='Enter your Username and Password',
            size_hint_x=0.8,
            snackbar_x='20dp',
            snackbar_y='20dp',
            pos_hint={'center_x': 0.5},
            duration=3,
        )
        self.snack.buttons = [
            MDFlatButton(text='I GOT IT', on_release=self.snack.dismiss, theme_text_color="Custom", text_color="orange")
        ]
        self.snack.open()

    def next_page(self):
        global loginer
        loginer = ""
        self.login_type = ""
        self.manager.transition.direction = 'left'
        tab_name = self.ids.login.get_current_tab().title
        if tab_name == 'USER':
            username = self.ids.username_user.text
            password = self.ids.user_password.get_pass()
            sql = f"""
            SELECT user_id, password FROM user WHERE user_id='{username}' AND password='{password}'
            """
            self.login_type = 'user'
        elif tab_name == 'STAFF':
            username = self.ids.username_staff.text
            password = self.ids.staff_password.get_pass()
            sql = f"""
            SELECT staff_id, password, type FROM staff WHERE staff_id='{username}' AND password='{password}'
            """

        conn = sqlite3.connect('library.db')
        c = conn.cursor()
        c.execute(sql)
        result = c.fetchone()
        if result is None:
            self.snack.text = 'INVALID USERNAME OR PASSWORD'
            self.snack.open()
            self.clear()
        else:
            if self.login_type != 'user':
                # get type of staff
                self.login_type = result[2]
            self.clear()
            self.manager.current = self.login_type
            loginer = result
            self.snack.dismiss()
        conn.close()

    def clear(self):
        self.ids.username_staff.text = ""
        self.ids.staff_password.clear()

        self.ids.username_user.text = ""
        self.ids.user_password.clear()


class WindowManager(MDScreenManager):
    pass


class DialogContent(BoxLayout):
    pass


class LibraryApp(MDApp):
    sound = None
    dialog = None

    def play_sound(self, *args):
        if not self.sound:
            self.sound = SoundLoader.load('musics/sound.wav')
            self.sound.loop = 1
            self.sound.play()

        else:
            self.sound.stop()
            self.sound = None

    def about(self):
        dismiss_btn = MDRaisedButton(text="OK")
        if not self.dialog:
            self.dialog = MDDialog(
                title="About me",
                type='custom',
                content_cls=DialogContent(),
                radius=[20, 7, 20, 7],
                buttons=[dismiss_btn],
            )
        dismiss_btn.bind(on_release=lambda x: self.dialog.dismiss())
        self.dialog.open()

    def build(self):
        self.theme_cls.theme_style = "Light"
        kv = Builder.load_file('styles/style.kv')
        return kv

    def on_start(self):
        self.play_sound()

    def logout(self):
        self.root.current = 'login'


if __name__ == '__main__':
    LibraryApp().run()
