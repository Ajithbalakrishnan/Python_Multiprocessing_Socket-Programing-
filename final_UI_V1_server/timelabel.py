from kivy.uix.label import Label
import time


class Time(Label):
    def updateTime(self,*args):
        self.text = time.asctime()


if __name__ == '__main__':
    from kivy.app import App
    from kivy.clock import Clock
    class TimeApp(App):
        def build(self):
            t=Time()
            Clock.schedule_interval(t.updateTime,1)
            return(t)

    TimeApp().run()