from django.core.management.base import BaseCommand
from apps.games.models import Game, GameCategory, GameItem

class Command(BaseCommand):
    help = 'Menambahkan data game awal (Free Fire, Mobile Legends, Genshin Impact, Roblox)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 MULAI SEED DATA GAMES...'))
        
        #free fire
        self.create_free_fire()
        self.stdout.write('-' * 40)
        
        #mobile legends
        self.create_mobile_legends()
        self.stdout.write('-' * 40)
        
        #genshin impact
        self.create_genshin()
        self.stdout.write('-' * 40)
        
        #roblox
        self.create_roblox()
        self.stdout.write('-' * 40)

        # honor of kings
        self.create_honor_of_kings()
        self.stdout.write('-' * 40)
        
        # call of duty
        self.create_call_of_duty()
        self.stdout.write('-' * 40)
        
        # delta force
        self.create_delta_force()
        self.stdout.write('-' * 40)
        
        # magic chess
        self.create_magic_chess()
        self.stdout.write('-' * 40)
        
        # point blank
        self.create_point_blank()
        self.stdout.write('-' * 40)
        
        # valorant
        self.create_valorant()
        self.stdout.write('-' * 40)
        
        # pubg mobile
        self.create_pubg_mobile()
        self.stdout.write('-' * 40)
        
        self.stdout.write(self.style.SUCCESS('✅ SEED DATA SELESAI!'))
    
    def create_free_fire(self):
        """Buat data Free Fire"""
        self.stdout.write('Membuat Free Fire...')
        
        # Buat game
        game, created = Game.objects.get_or_create(
            name="Free Fire",
            defaults={
                'description': "Layanan Top-Up Garena Free Fire terjamin aman. Isi diamond dan item eksklusif lainnya.",
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write('  ✓ Game Free Fire baru dibuat')
        else:
            self.stdout.write('  ○ Game Free Fire sudah ada, melanjutkan membuat items...')
        
        # Diamond category
        diamond_cat, _ = GameCategory.objects.get_or_create(
            game=game,
            name="Diamond",
            defaults={
                'description': "Mata uang utama Free Fire untuk membeli item, karakter, dan skin"
            }
        )
        
        # Membership category
        member_cat, _ = GameCategory.objects.get_or_create(
            game=game,
            name="Membership",
            defaults={
                'description': "Keanggotaan mingguan dan bulanan dengan berbagai bonus"
            }
        )
        
        # Diamond items
        items = [
            (5, 1500, False), (12, 3000, False), (50, 12000, False),
            (70, 17000, False), (91, 22000, False), (140, 34000, True),
            (355, 85000, True), (720, 172000, False), (1450, 347000, False),
            (2180, 522000, False), (3640, 870000, False), (7290, 1745000, False),
            (36500, 8725000, False), (73100, 17450000, False),
        ]
        
        for amount, price, popular in items:
            GameItem.objects.get_or_create(
                category=diamond_cat,
                name=f"{amount} Diamonds",
                defaults={
                    'amount': amount,
                    'price': price,
                    'is_popular': popular,
                    'is_active': True
                }
            )
        
        # Membership items
        memberships = [
            ("Member Mingguan", 1, 29000, True),
            ("Member Bulanan", 1, 89000, True),
            ("Mingguan Lite", 1, 15000, False),
            ("BP Card", 1, 65000, False),
            ("Body Pass Card", 1, 45000, False),
        ]
        
        for name, amount, price, popular in memberships:
            GameItem.objects.get_or_create(
                category=member_cat,
                name=name,
                defaults={
                    'amount': amount,
                    'price': price,
                    'is_popular': popular,
                    'is_active': True
                }
            )
        
        total_items = GameItem.objects.filter(category__game=game).count()
        self.stdout.write(self.style.SUCCESS(f'  ✓ Free Fire selesai ({total_items} items)'))
    
    def create_mobile_legends(self):
        """Buat data Mobile Legends"""
        self.stdout.write('Membuat Mobile Legends...')
        
        game, created = Game.objects.get_or_create(
            name="Mobile Legends",
            defaults={
                'description': "Top up Diamond Mobile Legends: Bang Bang dengan harga termurah dan proses cepat.",
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write('  ✓ Game Mobile Legends baru dibuat')
        else:
            self.stdout.write('  ○ Game Mobile Legends sudah ada, melanjutkan membuat items...')
        
        diamond_cat, _ = GameCategory.objects.get_or_create(
            game=game,
            name="Diamond",
            defaults={
                'description': "Mata uang utama Mobile Legends untuk membeli hero, skin, dan item"
            }
        )
        
        twilight_cat, _ = GameCategory.objects.get_or_create(
            game=game,
            name="Twilight Pass",
            defaults={
                'description': "Battle pass spesial dengan hadiah eksklusif"
            }
        )
        
        weekly_cat, _ = GameCategory.objects.get_or_create(
            game=game,
            name="Weekly Pass",
            defaults={
                'description': "Paket diamond mingguan dengan bonus"
            }
        )
        
        # Diamond items with bonus
        items = [
            ("5 Diamonds + 0 Bonus", 5, 1500, False),
            ("11 Diamonds + 1 Bonus", 12, 3300, False),
            ("17 Diamonds + 2 Bonus", 19, 5100, False),
            ("25 Diamonds + 3 Bonus", 28, 7500, False),
            ("40 Diamonds + 4 Bonus", 44, 12000, False),
            ("53 Diamonds + 6 Bonus", 59, 16000, False),
            ("77 Diamonds + 8 Bonus", 85, 23000, True),
            ("154 Diamonds + 16 Bonus", 170, 46000, True),
            ("217 Diamonds + 23 Bonus", 240, 65000, False),
            ("256 Diamonds + 40 Bonus", 296, 77000, False),
            ("367 Diamonds + 41 Bonus", 408, 110000, False),
            ("503 Diamonds + 65 Bonus", 568, 151000, False),
            ("774 Diamonds + 101 Bonus", 875, 232000, False),
            ("1708 Diamonds + 302 Bonus", 2010, 512000, False),
            ("4003 Diamonds + 827 Bonus", 4830, 1200000, False),
        ]
        
        for name, amount, price, popular in items:
            GameItem.objects.get_or_create(
                category=diamond_cat,
                name=name,
                defaults={
                    'amount': amount,
                    'price': price,
                    'is_popular': popular,
                    'is_active': True
                }
            )
        
        # Pass items
        GameItem.objects.get_or_create(
            category=twilight_cat,
            name="Twilight Pass",
            defaults={
                'amount': 1,
                'price': 149000,
                'is_popular': True,
                'is_active': True
            }
        )
        
        GameItem.objects.get_or_create(
            category=weekly_cat,
            name="Weekly Elite Bundle",
            defaults={
                'amount': 1,
                'price': 55000,
                'is_popular': True,
                'is_active': True
            }
        )
        
        GameItem.objects.get_or_create(
            category=weekly_cat,
            name="Monthly Epic Bundle",
            defaults={
                'amount': 1,
                'price': 189000,
                'is_popular': False,
                'is_active': True
            }
        )
        
        total_items = GameItem.objects.filter(category__game=game).count()
        self.stdout.write(self.style.SUCCESS(f'  ✓ Mobile Legends selesai ({total_items} items)'))
    
    def create_genshin(self):
        """Buat data Genshin Impact"""
        self.stdout.write('Membuat Genshin Impact...')
        
        game, created = Game.objects.get_or_create(
            name="Genshin Impact",
            defaults={
                'description': "Top up Genesis Crystal Genshin Impact. Dapatkan bonus crystal untuk setiap pembelian.",
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write('  ✓ Game Genshin Impact baru dibuat')
        else:
            self.stdout.write('  ○ Game Genshin Impact sudah ada, melanjutkan membuat items...')
        
        crystal_cat, _ = GameCategory.objects.get_or_create(
            game=game,
            name="Genesis Crystal",
            defaults={
                'description': "Mata uang premium Genshin Impact untuk membeli Primogem dan item lainnya"
            }
        )
        
        welkin_cat, _ = GameCategory.objects.get_or_create(
            game=game,
            name="Blessing of Welkin",
            defaults={
                'description': "Pass bulanan yang memberikan Primogem setiap hari"
            }
        )
        
        # Crystal items
        items = [
            ("60 Genesis Crystals", 60, 18000, False),
            ("300+30 Genesis Crystals", 330, 89000, True),
            ("980+110 Genesis Crystals", 1090, 289000, True),
            ("1980+260 Genesis Crystals", 2240, 569000, False),
            ("3280+600 Genesis Crystals", 3880, 949000, False),
            ("6480+1600 Genesis Crystals", 8080, 1879000, False),
        ]
        
        for name, amount, price, popular in items:
            GameItem.objects.get_or_create(
                category=crystal_cat,
                name=name,
                defaults={
                    'amount': amount,
                    'price': price,
                    'is_popular': popular,
                    'is_active': True
                }
            )
        
        # Welkin items
        GameItem.objects.get_or_create(
            category=welkin_cat,
            name="Blessing of Welkin Moon",
            defaults={
                'amount': 30,
                'price': 75000,
                'is_popular': True,
                'is_active': True
            }
        )
        
        total_items = GameItem.objects.filter(category__game=game).count()
        self.stdout.write(self.style.SUCCESS(f'  ✓ Genshin Impact selesai ({total_items} items)'))
    
    def create_roblox(self):
        """Buat data Roblox"""
        self.stdout.write('Membuat Roblox...')
        
        game, created = Game.objects.get_or_create(
            name="Roblox",
            defaults={
                'description': "Beli Roblox Gift Card untuk mendapatkan Robux. Redeem dan gunakan untuk membeli item di Roblox.",
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write('  ✓ Game Roblox baru dibuat')
        else:
            self.stdout.write('  ○ Game Roblox sudah ada, melanjutkan membuat items...')
        
        card_cat, _ = GameCategory.objects.get_or_create(
            game=game,
            name="Gift Card",
            defaults={
                'description': "Voucher Roblox yang bisa diredeem menjadi Robux"
            }
        )
        
        items = [
            ("Rp 50.000 Roblox Gift Card", 50000, 55000, True),
            ("Rp 65.000 Roblox Gift Card", 65000, 71000, False),
            ("Rp 100.000 Roblox Gift Card", 100000, 110000, True),
            ("Rp 200.000 Roblox Gift Card", 200000, 220000, False),
            ("Rp 500.000 Roblox Gift Card", 500000, 550000, False),
        ]
        
        for name, amount, price, popular in items:
            GameItem.objects.get_or_create(
                category=card_cat,
                name=name,
                defaults={
                    'amount': amount,
                    'price': price,
                    'is_popular': popular,
                    'is_active': True
                }
            )
        
        total_items = GameItem.objects.filter(category__game=game).count()
        self.stdout.write(self.style.SUCCESS(f'  ✓ Roblox selesai ({total_items} items)'))

    def create_honor_of_kings(self):
        """Buat data Honor of Kings (HOK)"""
        self.stdout.write('Membuat Honor of Kings...')
        
        game, created = Game.objects.get_or_create(
            name="Honor of Kings",
            defaults={
                'description': "Top up Token Honor of Kings termurah dan tercepat. Proses instan 24/7.",
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write('  ✓ Game Honor of Kings baru dibuat')
        else:
            self.stdout.write('  ○ Game Honor of Kings sudah ada, melanjutkan membuat items...')
        
        # Category
        token_cat, _ = GameCategory.objects.get_or_create(
            game=game,
            name="Tokens",
            defaults={
                'description': "Token untuk membeli hero, skin, dan item di Honor of Kings"
            }
        )
        
        # Items
        items = [
            ("80 Tokens", 80, 16000, False),
            ("240 Tokens", 240, 47000, False),
            ("400 Tokens", 400, 80000, False),
            ("560 Tokens", 560, 109000, False),
            ("2508 Tokens", 2508, 235000, True),
            ("4180 Tokens", 4180, 480000, False),
            ("8360 Tokens", 8360, 1599000, False),
        ]
        
        for name, amount, price, popular in items:
            GameItem.objects.get_or_create(
                category=token_cat,
                name=name,
                defaults={
                    'amount': amount,
                    'price': price,
                    'is_popular': popular,
                    'is_active': True
                }
            )
        
        total_items = GameItem.objects.filter(category__game=game).count()
        self.stdout.write(self.style.SUCCESS(f'  ✓ Honor of Kings selesai ({total_items} items)'))
    
    def create_call_of_duty(self):
        """Buat data Call of Duty: Mobile"""
        self.stdout.write('Membuat Call of Duty: Mobile...')
        
        game, created = Game.objects.get_or_create(
            name="Call of Duty: Mobile",
            defaults={
                'description': "Top up CP Call of Duty Mobile termurah. Proses cepat dan aman.",
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write('  ✓ Game Call of Duty: Mobile baru dibuat')
        else:
            self.stdout.write('  ○ Game Call of Duty: Mobile sudah ada, melanjutkan membuat items...')
        
        cp_cat, _ = GameCategory.objects.get_or_create(
            game=game,
            name="CP (COD Points)",
            defaults={
                'description': "Mata uang premium Call of Duty Mobile"
            }
        )
        
        items = [
            ("31 CP", 31, 4805, False),
            ("63 CP", 63, 9300, False),
            ("128 CP", 128, 18601, False),
            ("321 CP", 321, 46501, False),
            ("645 CP", 645, 93004, False),
            ("800 CP", 800, 112373, True),
            ("1373 CP", 1373, 186007, False),
            ("2060 CP", 2060, 279011, False),
            ("2750 CP", 2750, 355865, True),
            ("3564 CP", 3564, 465017, False),
            ("5619 CP", 5619, 683508, False),
            ("7656 CP", 7656, 930033, False),
            ("15312 CP", 15312, 1872540, False),
            ("38280 CP", 38280, 4681350, False),
            ("76560 CP", 76560, 9362700, False),
        ]
        
        for name, amount, price, popular in items:
            GameItem.objects.get_or_create(
                category=cp_cat,
                name=name,
                defaults={
                    'amount': amount,
                    'price': price,
                    'is_popular': popular,
                    'is_active': True
                }
            )
        
        total_items = GameItem.objects.filter(category__game=game).count()
        self.stdout.write(self.style.SUCCESS(f'  ✓ Call of Duty: Mobile selesai ({total_items} items)'))
    
    def create_delta_force(self):
        """Buat data Delta Force"""
        self.stdout.write('Membuat Delta Force...')
        
        game, created = Game.objects.get_or_create(
            name="Delta Force",
            defaults={
                'description': "Top up Delta Coins Delta Force Garena. Harga termurah se-Indonesia.",
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write('  ✓ Game Delta Force baru dibuat')
        else:
            self.stdout.write('  ○ Game Delta Force sudah ada, melanjutkan membuat items...')
        
        coins_cat, _ = GameCategory.objects.get_or_create(
            game=game,
            name="Delta Coins",
            defaults={
                'description': "Mata uang premium Delta Force"
            }
        )
        
        items = [
            ("18 + 1 Delta Coins", 19, 5208, False),
            ("30 + 2 Delta Coins", 32, 7813, False),
            ("Morphosis Supplies", 1, 15336, False),
            ("300 + 36 Delta Coins", 336, 23147, False),
            ("Operation Special", 1, 84197, True),
            ("Warfare Special", 1, 84197, True),
            ("All Modes", 1, 110237, False),
            ("680 + 105 Delta Coins", 785, 147272, False),
            ("1680 + 385 Delta Coins", 2065, 367746, False),
            ("3280 + 834 Delta Coins", 4114, 735204, False),
            ("12960 + 3888 Delta Coins", 16848, 2940815, False),
            ("19440 + 5832 Delta Coins", 25272, 4411222, False),
        ]
        
        for name, amount, price, popular in items:
            GameItem.objects.get_or_create(
                category=coins_cat,
                name=name,
                defaults={
                    'amount': amount,
                    'price': price,
                    'is_popular': popular,
                    'is_active': True
                }
            )
        
        total_items = GameItem.objects.filter(category__game=game).count()
        self.stdout.write(self.style.SUCCESS(f'  ✓ Delta Force selesai ({total_items} items)'))
    
    def create_magic_chess(self):
        """Buat data Magic Chess: Go Go"""
        self.stdout.write('Membuat Magic Chess: Go Go...')
        
        game, created = Game.objects.get_or_create(
            name="Magic Chess: Go Go",
            defaults={
                'description': "Top up Diamond Magic Chess: Go Go termurah dan tercepat.",
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write('  ✓ Game Magic Chess: Go Go baru dibuat')
        else:
            self.stdout.write('  ○ Game Magic Chess: Go Go sudah ada, melanjutkan membuat items...')
        
        diamond_cat, _ = GameCategory.objects.get_or_create(
            game=game,
            name="Diamond",
            defaults={
                'description': "Diamond untuk Magic Chess: Go Go"
            }
        )
        
        items = [
            ("5 Diamond", 5, 1575, True),
            ("40 + 4 Diamond", 44, 12600, False),
            ("217 + 23 Diamond", 240, 68250, False),
            ("774 + 101 Diamond", 875, 241500, False),
        ]
        
        for name, amount, price, popular in items:
            GameItem.objects.get_or_create(
                category=diamond_cat,
                name=name,
                defaults={
                    'amount': amount,
                    'price': price,
                    'is_popular': popular,
                    'is_active': True
                }
            )
        
        total_items = GameItem.objects.filter(category__game=game).count()
        self.stdout.write(self.style.SUCCESS(f'  ✓ Magic Chess: Go Go selesai ({total_items} items)'))
    
    def create_point_blank(self):
        """Buat data Point Blank"""
        self.stdout.write('Membuat Point Blank...')
        
        game, created = Game.objects.get_or_create(
            name="Point Blank",
            defaults={
                'description': "Top up PB Cash Point Blank termurah. Proses cepat dan aman.",
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write('  ✓ Game Point Blank baru dibuat')
        else:
            self.stdout.write('  ○ Game Point Blank sudah ada, melanjutkan membuat items...')
        
        pb_cat, _ = GameCategory.objects.get_or_create(
            game=game,
            name="PB Cash",
            defaults={
                'description': "Mata uang premium Point Blank"
            }
        )
        
        items = [
            ("1,200 PB Cash", 1200, 10000, True),
            ("30,000 PB Cash", 30000, 327955, False),
            ("60,000 PB Cash", 60000, 655909, False),
        ]
        
        for name, amount, price, popular in items:
            GameItem.objects.get_or_create(
                category=pb_cat,
                name=name,
                defaults={
                    'amount': amount,
                    'price': price,
                    'is_popular': popular,
                    'is_active': True
                }
            )
        
        total_items = GameItem.objects.filter(category__game=game).count()
        self.stdout.write(self.style.SUCCESS(f'  ✓ Point Blank selesai ({total_items} items)'))
    
    def create_valorant(self):
        """Buat data Valorant"""
        self.stdout.write('Membuat Valorant...')
        
        game, created = Game.objects.get_or_create(
            name="Valorant",
            defaults={
                'description': "Top up VP Valorant termurah. Proses cepat dan aman.",
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write('  ✓ Game Valorant baru dibuat')
        else:
            self.stdout.write('  ○ Game Valorant sudah ada, melanjutkan membuat items...')
        
        vp_cat, _ = GameCategory.objects.get_or_create(
            game=game,
            name="VP (Valorant Points)",
            defaults={
                'description': "Mata uang premium Valorant"
            }
        )
        
        items = [
            ("475 VP", 475, 56000, True),
            ("1000 VP", 1000, 112000, True),
            ("2050 VP", 2050, 224000, False),
            ("3650 VP", 3650, 389000, False),
            ("5350 VP", 5350, 1099000, False),
        ]
        
        for name, amount, price, popular in items:
            GameItem.objects.get_or_create(
                category=vp_cat,
                name=name,
                defaults={
                    'amount': amount,
                    'price': price,
                    'is_popular': popular,
                    'is_active': True
                }
            )
        
        total_items = GameItem.objects.filter(category__game=game).count()
        self.stdout.write(self.style.SUCCESS(f'  ✓ Valorant selesai ({total_items} items)'))
    
    def create_pubg_mobile(self):
        """Buat data PUBG Mobile"""
        self.stdout.write('Membuat PUBG Mobile...')
        
        game, created = Game.objects.get_or_create(
            name="PUBG Mobile",
            defaults={
                'description': "Top up UC PUBG Mobile termurah. Proses instan 24/7.",
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write('  ✓ Game PUBG Mobile baru dibuat')
        else:
            self.stdout.write('  ○ Game PUBG Mobile sudah ada, melanjutkan membuat items...')
        
        uc_cat, _ = GameCategory.objects.get_or_create(
            game=game,
            name="UC (Unknown Cash)",
            defaults={
                'description': "Mata uang premium PUBG Mobile"
            }
        )
        
        items = [
            ("60 UC", 60, 16622, True),
            ("325 UC", 325, 83782, False),
            ("660 UC", 660, 167732, True),
            ("1800 UC", 1800, 419582, False),
        ]
        
        for name, amount, price, popular in items:
            GameItem.objects.get_or_create(
                category=uc_cat,
                name=name,
                defaults={
                    'amount': amount,
                    'price': price,
                    'is_popular': popular,
                    'is_active': True
                }
            )
        
        total_items = GameItem.objects.filter(category__game=game).count()
        self.stdout.write(self.style.SUCCESS(f'  ✓ PUBG Mobile selesai ({total_items} items)'))