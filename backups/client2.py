if 'fight' in item:
                    Clock.schedule_once(lambda dt: self.root.get_screen('main').animate(1))
                    time.sleep(1)
                    print('fighting')
                    print(1)
                    enemy = item.removeprefix('fight ')
                    enemy_max_hp = self.enemies.get(enemy).get('hp')
                    enemy_actual_hp = self.hps.get(enemy)
                    enemy_attack = self.enemies.get(enemy).get('attack')
                    enemy_defense = self.enemies.get(enemy).get('defense')
                    player_max_hp = self.player_stats.get('hp')
                    player_actual_hp = self.hps.get('player')
                    player_body = self.equipped.get('body')
                    player_right = self.equipped.get('right')
                    player_armor_type = self.equippables.get(player_body)
                    player_weapon_type = self.equippables.get(player_right)
                    if player_armor_type == 'strength':
                        player_defense = self.equipment_stats.get(player_body)
                    if player_armor_type == 'dexterity':
                        player_defense = self.player_stats.get('dexterity')
                    if player_weapon_type == 'strength':
                        player_attack = self.player_stats.get('strength')
                    if player_weapon_type == 'dexterity':
                        player_attack = self.player_stats.get('dexterity')
                    enemy_hits = (enemy_attack + random.randint(-5, 5)) - (player_defense + random.randint(-5, 5)) > 0
                    player_hits = (player_attack + random.randint(-5, 5)) - (enemy_defense + random.randint(-5,5)) > 0
                    new_hps = dict(self.hps)
                    print('armor' + player_armor_type)
                    print('weapon' + player_weapon_type)
                    if enemy_hits:
                        new_hps['player'] -= enemy_attack
                    if player_hits:
                        new_hps[enemy] -= player_attack

                    if self.hps['player'] <= 0 or self.hps[enemy] <= 0:
                        self.idling = False
                        new_hps['player'] = player_max_hp
                        new_hps[enemy] = enemy_max_hp
                    def apply_hp_update(dt):
                        self.hps = new_hps
                    Clock.schedule_once(apply_hp_update)
                    print(self.hps)