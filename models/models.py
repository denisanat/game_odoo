from odoo import models, fields, api


class player( models.Model ):
    _name = 'game.player'
    _description = 'The players of the game'

    name = fields.Char( required = True )
    th_level = fields.Integer( string = "Nivel de Ayuntamiento", default = "1", help = "El nivel del ayuntamiento indica hasta que nivel puedes mejorar el resto de estructuras" )

    gold = fields.Integer( string = "Oro", default = 10000, readonly = True )
    elixir = fields.Integer( string = "Elixir", default = 10000, readonly = True )
    dark_elixir = fields.Integer( string = "Elixir oscuro", default = 0, readonly = True )

    buildings = fields.One2many( comodel_name = 'game.building', inverse_name = 'player', string = "Edificios" )
    badges = fields.Many2many( comodel_name = 'game.badge', string = 'Insignias' )
    clan = fields.Many2one( "game.clan" )
    clanFriends = fields.One2many( 'game.player', related = 'clan.players', readonly = True, string = 'Compañeros de clan' )
    clanColor = fields.Selection([('1', 'Azul'), ('2', 'Amarillo')], string='Color del Clan', related='clan.color', store=True, readonly=True)


class building_type( models.Model ):
    _name = 'game.building_type'
    _description = "The types of a building"

    name = fields.Char()
    gold_production = fields.Float()
    elixir_production = fields.Float()
    dark_elixir_production = fields.Float()
    upgrade_cost = fields.Integer()


class building( models.Model ):
    _name = 'game.building'
    _description = "Buildings in the village"

    name = fields.Char( compute = '_get_production' )
    type = fields.Many2one( 'game.building_type', required = True )
    level = fields.Integer( default = 1, string = "Nivel" )
    update_percent = fields.Float( default = 0 )
    gold_production = fields.Float( compute = '_get_production', string = "Oro por hora" )
    elixir_production = fields.Float( string = "Elixir por hora", compute = '_get_production' )
    dark_elixir_production = fields.Float( string = "Elixir oscuro por hora", compute = '_get_production' )
    upgrade_cost = fields.Integer( string = "Coste de mejora", compute = '_get_production' )

    player = fields.Many2one( "game.player", ondelete = "restrict" )

    @api.depends( 'type', 'level' )
    def _get_production( self ):
        for b in self:
            b.name = b.type.name
            b.gold_production = b.type.gold_production
            b.elixir_production = b.type.elixir_production
            b.dark_elixir_production = b.type.dark_elixir_production
            b.upgrade_cost = b.type.upgrade_cost


class badge( models.Model ):
    _name = 'game.badge'
    _description = 'Badges that players can put to personalize their profiles'

    name = fields.Char()
    text = fields.Text()

    players = fields.Many2many( comodel_name='game.player' )

class clan( models.Model ):
    _name = 'game.clan'
    _description = 'Clans where anyone can join'

    name = fields.Char()
    color = fields.Selection([('1', 'Azul'), ('2', 'Amarillo')], required = True)
    
    players = fields.One2many( comodel_name = 'game.player', inverse_name = 'clan' )
    




    









#     value2 = fields.Float(compute="_value_pc", store=True)
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
