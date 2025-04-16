    def show_start_window(self, event):
        arcade.play_sound(self.start)
        self.game_settings = True
        self.menu = False

        self.managers = UIManager()
        self.managers.enable()
        box = arcade.gui.UIBoxLayout()
        ui_slider = UISlider(value=self.players_count, width=300, height=50, max_value=4, min_value=1)
        label = UILabel(text=f"игроков:{ui_slider.value:1.0f}")

        @ui_slider.event()
        def on_change(event: UIOnChangeEvent):
            if self.game_settings:
                label.text = f"игроков:{ui_slider.value:1.0f}"
                label.fit_content()
                self.players_count = round(ui_slider.value)

        box.add(child=label.with_space_around(left=100,bottom=10))
        box.add(child=ui_slider.with_space_around(left=100,bottom=20))
        debug_mode = arcade.gui.UITextureButton(
            texture=arcade.load_texture(":resources:onscreen_controls/flat_dark/unchecked.png"))
        label_d = UILabel(text=f"режим отладки")
        back = arcade.gui.UITextureButton(
            texture=arcade.load_texture(":resources:onscreen_controls/flat_dark/left.png"), scale=0.5)
        sound = arcade.gui.UITextureButton(
            texture=arcade.load_texture(":resources:onscreen_controls/flat_dark/music_on.png"))

        @sound.event("on_click")
        def on_change(event):
            if self.game_settings:
                self.music = not self.music
                if self.debug:
                    sound.texture = arcade.load_texture(":resources:onscreen_controls/flat_dark/music_on.png")
                else:
                    sound.texture = arcade.load_texture(":resources:onscreen_controls/flat_dark/music_off.png")

        @back.event("on_click")
        def back_f(event):
            if self.game_settings:
                self.set_menu()

        @debug_mode.event("on_click")
        def on_change(event):
            if self.game_settings:
                self.debug = not self.debug
                if self.debug:
                    debug_mode.texture = arcade.load_texture(":resources:onscreen_controls/flat_dark/checked.png")
                else:
                    debug_mode.texture = arcade.load_texture(":resources:onscreen_controls/flat_dark/unchecked.png")

        replay_cap = arcade.gui.UITextureButton(texture=arcade.load_texture(":resources:onscreen_controls/flat_dark/unchecked.png"))
        @replay_cap.event("on_click")
        def on_change(event):
            if self.game_settings:
                self.replay_state['record'] = not self.replay_state['record']
                if self.replay_state['record']:
                    replay_cap.texture = arcade.load_texture(":resources:onscreen_controls/flat_dark/checked.png")
                else:
                    replay_cap.texture = arcade.load_texture(":resources:onscreen_controls/flat_dark/unchecked.png")
        replay_play = arcade.gui.UITextureButton(texture=arcade.load_texture(":resources:onscreen_controls/flat_dark/unchecked.png"))
        @replay_play.event("on_click")
        def on_change(event):
            if self.game_settings:
                self.replay_state['play'] = not self.replay_state['play']
                if self.replay_state['play']:
                    replay_play.texture = arcade.load_texture(":resources:onscreen_controls/flat_dark/checked.png")
                else:
                    replay_play.texture = arcade.load_texture(":resources:onscreen_controls/flat_dark/unchecked.png")


        # self.managers.add(UIAnchorWidget(child=sound, align_y=90)) #TODO add sound controller
        box.add(child=label_d.with_space_around(left=100,bottom=20))
        box.add(child=debug_mode.with_space_around(left=100,bottom=20))
        box.add(child=UILabel(text="захват повтора").with_space_around(left=100,bottom=10))
        box.add(child=replay_cap.with_space_around(left=100,bottom=20))
        box.add(child=UILabel(text="просмотр повтора").with_space_around(left=100,bottom=10))
        box.add(child=replay_play.with_space_around(left=100,bottom=20))
        label_ai = UILabel(text="в этой версии нет ботов")
        box.add(child=label_ai.with_space_around(left=100,bottom=20))
        box.add(child=back.with_space_around(left=100,bottom=20))
        w, h = super().width, super().height
        self.managers.add(UIAnchorWidget(anchor_x="center_x", anchor_y="center_y", child=box))
 
    def set_menu(self):
        self.game = False
        self.menu = True
        self.managers.disable()
        self.manager.enable()
        self.game_settings = False

    def menu_music(self):
        mus = arcade.play_sound(self.music_in_menu)
        if not self.music:
            arcade.stop_sound(mus)

   def on_start(self, event):
        self.game_settings = False
        self.frame = 0
        if self.menu:
            self.cur_player = 0
            self.player_list = []
            self.players = []
            self.setup()
            arcade.play_sound(self.start)
            for player in range(len(self.players)):
                id = int(player)
                player = self.players[id]
                player['sprite'].center_x, player['sprite'].center_y = self.coordinates[id]
                player['speed'] = 0
                player['current_angle'] = 90
            self.game = True
            self.menu = False
            self.start_time = time.time()

    def exit(self, event):
        arcade.play_sound(self.start)
        if self.menu:
            arcade.close_window()

