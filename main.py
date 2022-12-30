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
from kivymd.uix.list import ThreeLineAvatarIconListItem,IconRightWidget


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

        snack = Snackbar(text=f"Welcome Dear {result[1]}!!!",
                         snackbar_x='30dp',
                         snackbar_y='30dp',
                         radius=[10, 10, 10, 10],
                         size_hint_x=0.5,
                         pos_hint={'center_x': 0.5},
                         duration=10
                         )
        snack.buttons = [
            MDFlatButton(text='DISMISS', on_release=snack.dismiss, theme_text_color="Custom", text_color="orange")]
        snack.open()


class EmployeeScreen(MDScreen):
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
        result = self.get_loginer()
        snack = Snackbar(text=f"Welcome dear {result[1]}!!!",
                         snackbar_x='30dp',
                         snackbar_y='30dp',
                         radius=[10, 10, 10, 10],
                         size_hint_x=0.5,
                         pos_hint={'center_x': 0.5},
                         duration=10
                         )
        snack.buttons = [
            MDFlatButton(text='DISMISS', on_release=snack.dismiss, theme_text_color="Custom", text_color="orange")]
        snack.open()


class AdminScreen(MDScreen):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dropdown=MDDropdownMenu()

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
                         duration=10
                         )
        snack.buttons = [
            MDFlatButton(text='DISMISS', on_release=snack.dismiss, theme_text_color="Custom", text_color="orange")]
        snack.open()

    def search_user(self):
        result_list=self.ids.result_search_user
        result_list.clear_widgets()
        name=self.ids.search_by_name.text.strip()
        id=self.ids.search_by_id.text.strip()
        conn=sqlite3.connect("library.db")
        c=conn.cursor()
        if name and id:
            sql=f"""
                SELECT * FROM user
                WHERE 
                user_id LIKE "%{id}%" AND
                name LIKE "%{name}%" 
            """
        elif name:
            sql=f"""
                SELECT * FROM user
                WHERE 
                name LIKE "%{name}%" 
            """
        elif id:
            sql=f"""
                SELECT * FROM user
                WHERE 
                user_id LIKE "%{id}%" 
            """
        else:
            return
        c.execute(sql)
        while result:=c.fetchone():
            result_list.add_widget(
                ThreeLineAvatarIconListItem(
                    IconRightWidget(
                        icon="account"
                    ),
                    text=f"ID: {result[0]} - NAME: {result[1]} - PHONE: {result[4]}",
                    secondary_text= f"FINE: {result[5]} - EXPIRE_DATE: {result[6]}",
                    tertiary_text= f"ADDRESS: {result[2]}",
                )
            )
        c.close()

    def suggestion(self,obj):
        items=list()
        self.dropdown.dismiss()
        name=self.ids.search_by_name.text.strip()
        id=self.ids.search_by_id.text.strip()

        conn=sqlite3.connect("library.db")
        c=conn.cursor()
        if name and id:
            sql=f"""
                SELECT * FROM user
                WHERE 
                user_id LIKE "%{id}%" AND
                name LIKE "%{name}%" 
            """
        elif name:
            sql=f"""
                SELECT * FROM user
                WHERE 
                name LIKE "%{name}%" 
            """
        elif id:
            sql=f"""
                SELECT * FROM user
                WHERE 
                user_id LIKE "%{id}%" 
            """
        else:
            return
        c.execute(sql)
        i=0
        while 1:
            result=c.fetchone()
            if result is None or i==3:
                break
            items.append(                
                {
                "viewclass": "OneLineListItem",
                "height": dp(56),
                "text": f"NAME: {result[1]} -- ID: {result[0]}",
                "on_release":lambda x=result: self.set_values(x)
                })
            i+=1
        if items:
            self.dropdown.items=items
            self.dropdown.caller=obj
            self.dropdown.width_mult=5
            self.dropdown.position='top'
            self.dropdown.open()
        else:
            self.dropdown.dismiss()
        conn.close()

    def set_values(self,result):
        result_list=self.ids.result_search_user
        result_list.clear_widgets()
        self.ids.search_by_name.text=str(result[1])
        self.ids.search_by_id.text=str(result[0])
        self.dropdown.dismiss()
        result_list.add_widget(
            ThreeLineAvatarIconListItem(
                IconRightWidget(
                    icon="account"
                ),
                text=f"ID: {result[0]} - NAME: {result[1]} - PHONE: {result[4]}",
                secondary_text= f"FINE: {result[5]} - EXPIRE_DATE: {result[6]}",
                tertiary_text= f"ADDRESS: {result[2]}",
            )
        )

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
            duration=5,
        )
        self.snack.buttons = [
            MDFlatButton(text='I GOT IT', on_release=self.snack.dismiss, theme_text_color="Custom", text_color="orange")
        ]
        self.snack.open()

    def next_page(self):
        global loginer
        self.manager.transition.direction = 'left'
        tab_name = self.ids.login.get_current_tab().title
        if tab_name == 'USER':
            username = self.ids.username_user.text
            password = self.ids.user_password.get_pass()
            sql = f"""
            SELECT user_id, password FROM user WHERE user_id='{username}' AND password='{password}'
            """
            self.login_type = 'user'
        else:
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
