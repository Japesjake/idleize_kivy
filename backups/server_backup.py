        # self.set_address('JpJab')
        self.thread.start()
    # def set_address(self, player_name):
    #     with sqlite3.connect('data.db') as db_connection:
    #         cursor = db_connection.cursor()
    #         cursor.execute('UPDATE Player SET address = ? WHERE name = ?', (self.addr_concat,player_name))
    #         db_connection.commit()
    #         db_connection.close()