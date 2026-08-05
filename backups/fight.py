if 'fight' in item:
    Clock.schedule_once(lambda dt: self.root.get_screen('main').animate(1))
    time.sleep(1)
    print('fighting')
    print(1)
    enemy = item.removeprefix('fight ')
    enemy_base_hp = self.enemies.get(enemy).get('hp')
    enemy_actual_hp = self.hps.get(enemy)
    enemy_attack = self.enemies.get(enemy).get('attack')
    enemy_defense = self.enemies.get(enemy).get('defense')
    player_max_hp = self.player_stats.get('hp')
    player_actual_hp = self.hps.get('player')
    player_armor_type = self.player_stats.get('armor type')
    player_weapon_type = self.player_stats.get('weapon type')
    if player_armor_type == 'strength':
        player_defense = self.player_stats.get('defense')
    if player_armor_type == 'dexterity':
        player_defense = self.player_stats.get('dexterity')
    if player_weapon_type == 'strength':
        player_attack = self.player_stats.get('strength')
    if player_weapon_type == 'dexterity':
        player_attack = self.player_stats.get('dexterity')
    enemy_hits = (enemy_attack + random.randint(-5, 5)) - (player_defense + random.randint(-5, 5)) > 0
    player_hits = (player_attack + random.randint(-5, 5)) - (enemy_defense + random.randint(-5,5)) > 0
    new_hps = dict(self.hps)
    if enemy_hits:
        new_hps['player'] -= enemy_attack
    if player_hits:
        new_hps[enemy] -= player_attack
    def apply_hp_update(dt):
        self.hps = new_hps
    Clock.schedule_once(apply_hp_update)
    if self.hps['player'] <= 0 or self.hps[enemy] <= 0:
        self.idling = False
        break
    print(self.hps)



    enemy = item.removeprefix('fight ')
                        enemy_attack = self.enemies.get(enemy).get('attack')
                        enemy_damage = self.enemies.get(enemy).get('damage')
                        enemy_defense = self.enemies.get(enemy).get('defense')
                        equipped_weapon = self.equipped.get('right')
                        equipped_armor = self.equipped.get('body')
                        equipped_weapon_type = self.equippables.get(equipped_weapon)
                        equipped_armor_type = self.equippables.get(equipped_armor)
                        ### Strength Weapon ###
                        if equipped_weapon_type == 'strength':
                            player_attack = self.player_stats.get('strength')
                            player_damage = self.equipment_stats.get(equipped_weapon)
                        ### Dexterity Weapon ###
                        elif equipped_weapon_type == 'dexterity':
                            player_attack = self.player_stats.get('dexterity')
                            player_damage = self.equipment_stats.get(equipped_weapon)
                        if equipped_weapon == '':
                            player_attack = 0
                            player_damage = 0
                        ### Strength Armor ###
                        if equipped_armor_type == 'strength':
                            player_defense = self.equipment_stats.get(equipped_armor)
                        ### Dexterity Armor ###
                        elif equipped_armor_type == 'dexterity':
                            player_defense = self.player_stats.get('dexterity')
                            modifier = self.equipment_stats.get(equipped_weapon)
                            player_defense += modifier
                        if equipped_armor == '':
                            player_defense = 0
                            player_damage = 0
                        enemy_hits = (enemy_attack + random.randint(-5, 5)) - (player_defense + random.randint(-5, 5)) > 0
                        player_hits = (player_attack + random.randint(-5, 5)) - (enemy_defense + random.randint(-5,5)) > 0