from kivy_garden.mapview import MapView
from kivymd.app import MDApp
from kivy_garden.mapview import MapMarkerPopup
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.utils import platform
from kivymd.uix.dialog import MDDialog


from kivy.lang import Builder
Builder.load_file("./main.kv") # loading a ".kv" file instead of making file like the class name

class MarketMarker(MapMarkerPopup):
    source = "marker.png"
    def on_release(self):
        pass

class Maps_view(MapView):
    getting_markets_timer = None

    def start_getting_markets_in_fov(self):
        # After one second, get the markets in the field of view
        try:
            self.getting_markets_timer.cancel()
        except:
            pass
        self.getting_markets_timer = Clock.schedule_once(self.add_market, 1)

    def add_market(self, *args):
        if platform == 'android':
            from android.permissions import Permission, request_permissions
            def callback(permission, results):
                if all([res for res in results]):
                    print("Got all permissions")
                    from plyer import gps
                    gps.configure(on_location=self.update_blinker_position, on_status=self.on_auth_status)
                    gps.start(minTime=1000, minDistance=0)
                else:
                    print("Did not get all permissions")

            request_permissions([Permission.ACCESS_COARSE_LOCATION, Permission.ACCESS_FINE_LOCATION], callback)

        if platform == 'ios':
            from plyer import gps
            gps.configure(on_location=self.update_blinker_position, on_status=self.on_auth_status)
            gps.start(minTime=1000, minDistance=0)


    def update_blinker_position(self, *args, **kwargs):
        my_lat = kwargs['lat']
        my_lon = kwargs['lon']
        self.ids.hello_map.lat = my_lat
        self.ids.hello_map.lon = my_lon
        print("GPS POSITION", my_lat, my_lon)
        # Update GpsBlinker position
        marker = MarketMarker(lat=my_lat, lon=my_lon)
        self.add_widget(marker)

        # Center map on gps
        if not self.has_centered_map:
            map = App.get_running_app().root.ids.mapview
            map.center_on(my_lat, my_lon)
            self.has_centered_map = True

    def on_auth_status(self, general_status, status_message):
        if general_status == 'provider-enabled':
            pass
        else:
            self.open_gps_access_popup()

    def open_gps_access_popup(self):
        dialog = MDDialog(title="GPS Error", text="You need to enable GPS access for the app to function properly")
        dialog.size_hint = [.8, .8]
        dialog.pos_hint = {'center_x': .5, 'center_y': .5}
        dialog.open()

class MyApp(App):
    def build(self):
        return Maps_view()

MyApp().run()













