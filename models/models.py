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


class building( models.Model ):
    _name = 'game.building'
    _description = "Buildings in the village"

    name = fields.Char( required = True )
    level = fields.Integer( default = "1", string = "Nivel", readonly = True )

    player = fields.Many2one( "game.player", ondelete = "restrict" )


class badge( models.Model ):
    _name = 'game.badge'
    _description = 'Badges that players can put to personalize their profiles'

    name = fields.Char()

    players = fields.Many2many( comodel_name='game.player' )




    









#     value2 = fields.Float(compute="_value_pc", store=True)
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
