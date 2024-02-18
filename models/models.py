from odoo import models, fields, api
import math
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class player( models.Model ):
    _name = 'game.player'
    _description = 'The players of the game'

    name = fields.Char( required = True )
    th_level = fields.Integer( string = "Nivel de Ayuntamiento", default = "1", help = "El nivel del ayuntamiento indica hasta que nivel puedes mejorar el resto de estructuras" )

    gold = fields.Float( string = "Oro", default = 10000, readonly = True )
    elixir = fields.Float( string = "Elixir", default = 10000, readonly = True )
    dark_elixir = fields.Float( string = "Elixir oscuro", default = 0, readonly = True )

    gold_production = fields.Float( string = "Oro por hora", compute = "_get_total_production" )

    buildings = fields.One2many( comodel_name = 'game.building', inverse_name = 'player', string = "Edificios" )
    troops = fields.One2many( comodel_name = 'game.troop', inverse_name = 'player', string = "Ejercito" )
    badges = fields.Many2many( comodel_name = 'game.badge', string = 'Insignias' )
    clan = fields.Many2one( "game.clan" )
    clanFriends = fields.One2many( 'game.player', related = 'clan.players', readonly = True, string = 'Compañeros de clan' )
    clanColor = fields.Selection([('1', 'Azul'), ('2', 'Amarillo')], string='Color del Clan', related='clan.color', store=True, readonly=True)

    def upgrade_th(self):
        for p in self:
            p.th_level = p.th_level + 1

    @api.constrains('buildings')
    def _max_level_building(self):
        for p in self:
            for b in p.buildings:
                if b.level > p.th_level:
                    raise ValidationError("El nivel de tus edificios no puede sobrepasar el del ayuntamiento")
            
    def _get_total_production( self ):
        for p in self:
            p.gold_production = sum( p.buildings.mapped('gold_production'))


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

    player = fields.Many2one( "game.player", ondelete = "cascade" )

    @api.depends( 'type', 'level' )
    def _get_production( self ):
        for b in self:
            b.name = b.type.name
            b.gold_production = b.type.gold_production * b.level
            b.elixir_production = b.type.elixir_production * b.level
            b.dark_elixir_production = b.type.dark_elixir_production * b.level
            b.upgrade_cost = b.type.upgrade_cost * b.level


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
    color = fields.Selection([('1', 'Azul'), ('2', 'Amarillo')], required = True )
    categoria = fields.Char( compute = '_get_categoria' )
    
    players = fields.One2many( comodel_name = 'game.player', inverse_name = 'clan' )

    def _get_categoria( self ):
        for c in self:
            if len( c.players.filtered( lambda p: p.th_level > 3 )) > 3:
                c.categoria = "Clan de nivel alto"
            else:
                c.categoria = "Clan de nivel bajo"
    

class battle( models.Model ):
    _name = 'game.battle'
    _description = 'Battles between two players'

    name = fields.Char()
    player1 = fields.Many2one( 'game.player', domain="[('id','!=',player2)]", required = True )
    player2 = fields.Many2one( 'game.player', domain="[('id','!=',player1)]", required = True )
    start = fields.Datetime( default = lambda self: fields.Datetime.now() )
    end = fields.Datetime( compute = '_set_end_date' )
    total_time = fields.Integer( compute = '_set_end_date' )
    remaining_time = fields.Char( compute = '_set_end_date' )
    progress = fields.Float(compute='_set_end_date')

    @api.depends('start')
    def _set_end_date(self):
        for b in self:
            date_start = fields.Datetime.from_string(b.start)
            date_end = date_start + timedelta(hours=2)
            b.end = fields.Datetime.to_string(date_end)
            b.total_time = (date_end - date_start).total_seconds() / 60
            remaining = relativedelta(date_end, datetime.now())
            b.remaining_time = str(remaining.hours) + ":" + str(remaining.minutes) + ":" + str(remaining.seconds)
            passed_time = (datetime.now() - date_start).total_seconds()
            b.progress = (passed_time * 100) / (b.total_time * 60)
            if b.progress > 100:
                b.progress = 100
                b.remaining_time = '00:00:00'


    class troop( models.Model ):
        _name = 'game.troop'
        _description = 'The troops that every player has'

        name = fields.Char( compute = '_get_unit', string = "Nombre" )
        unit = fields.Many2one( 'game.unit', required = True )
        health = fields.Float( compute = '_get_unit', string = "Vida" )
        damage = fields.Float( compute = '_get_unit', string = "Daño" )
        quantity = fields.Integer( required = True, default = 1, string = "Cantidad" )
        player = fields.Many2one( 'game.player', ondelete = "cascade" )
        cost = fields.Float( compute = '_get_unit', string = "Coste" )

        @api.depends( 'unit' )
        def _get_unit( self ):
            for t in self:
                t.name = t.unit.name
                t.health = t.unit.health
                t.damage = t.unit.health
                t.cost = t.unit.cost


    class unit( models.Model ):
        _name = 'game.unit'
        _description = 'Each unit'

        name = fields.Char()
        health = fields.Float()
        damage = fields.Float()
        cost = fields.Float()




    









#     value2 = fields.Float(compute="_value_pc", store=True)
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
