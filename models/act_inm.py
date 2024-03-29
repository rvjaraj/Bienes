# -*- coding: utf-8 -*-
##############################################################################
#   SICAF - Copyright  2019
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning, DeferredException, UserError, MissingError


def compute_default_codigo(self, tam):
    listado = self.env[self._name].search([])
    numero = str(int(listado[-1].codigo if listado else '0') + 1)
    return numero.zfill(tam)


class Material(models.Model):
    _name = 'act.inm.material'
    _description = 'Activos - Bienes - Inmueble - Material'
    # _rec_name = ''
    codigo = fields.Char('Código', required=True, size=4, default=lambda self: compute_default_codigo(self, 4),
                         help='Codigo del Detalle')
    material = fields.Char('Material', required=True, help='Material')
    descripcion = fields.Char('Descripcion', required=True, help='Descripcion del tipo material construccion')

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.material + ' | ' + record.descripcion))
        return result


class Inmueble(models.Model):
    _name = 'act.inm.inmueble'
    _description = 'Activos - Bienes - Inmueble'
    # _rec_name = ''
    currency_id = fields.Many2one('res.currency', "Currency")
    codigo = fields.Char('Código', required=True, size=4, default=lambda self: compute_default_codigo(self, 4),
                         help='Codigo del Inmueble')

    identificación = fields.Char('Identificación', required=True, help='Serie del Bien')
    caracteristicas_unicas = fields.Char('Características únicas', required=True, help='Modelo del Bien')
    material_contruccion = fields.Many2one('act.inm.material', string='Material de construcción', required=True,
                                           help='Marca del bien')

    pro_reg_municipio = fields.Char('Propietario registrado en el Municipio', required=True,
                                    help='Propietario registrado en el Municipio')
    clave_catastral = fields.Char('Clave Catastral', required=True, help='Clave Catastral')
    num_predio = fields.Char('Numero de predio', required=True, help='Nunmero de predio')
    valor_avaluo = fields.Monetary('Valor avalúo Municipal', default=0.0, required=True, help='Valor avalúo Municipal')
    anio_avaluo = fields.Char('Año avalúo Municipal', required=True, help='Año avalúo Municipal', size=4)
    area_predio = fields.Float('Área del Predio m2', digits=(6, 2), required=True)
    area_contruccion = fields.Float('Área de Construcción m2', digist=(6, 2), required=True)
    num_pisos = fields.Char('Número de pisos', default=1, required=True, size=4)
    num_escritura = fields.Char('Número de escritura', required=True, help='Número de escritura')
    fecha_escritura = fields.Date('Fecha de la Escritura', required=False, help='Fecha de la Escritura')
    notari = fields.Char('Notaria', requiered=True, help='Notaria', size=4)
    beneficiario = fields.Char('Beneficiario', required=False, help=' Beneficiario ')
    fecha_contrato = fields.Date('Fecha Contrato', required=False, help='Fecha del Contrato')
    fecha_duracion = fields.Date('Fecha: Tiempo de duración', required=False, help='Tiempo de duración')
    canon_actua = fields.Monetary('Monto | Canon Actual', default=0.0, required=False, help='Monto | Canon Actual')
    direccion_id = fields.Many2one('act.inm.direccion', string='Dirección', required=True,
                                   help='Dirección del inmueble ')

    dato_icorrecto = fields.Boolean("Dato Icorrecto", default=False, required=True)

    @api.onchange('fecha_duracion', 'fecha_contrato')
    def _change_fecha_durecuion(self):
        if self.fecha_duracion and self.fecha_contrato:
            if self.fecha_contrato > self.fecha_duracion:
                self.fecha_duracion = False
                return {
                    'warning': {
                        'title': 'Fecha Icorrecta!',
                        'message': 'La <b>Fecha: Tiempo de duración</b> no puede ser menor a la <b> Fecha Contrato</b>',
                        'type': 'notification'}
                }


class Direccion(models.Model):
    _name = 'act.inm.direccion'
    _description = 'Activos - Bienes - Inmuebles - Dirección '
    # _rec_name = ''
    codigo = fields.Char('Código', required=True, size=20, default=lambda self: compute_default_codigo(self, 4),
                         help='Código Direccion del Inmueble')
    parroquia_id = fields.Many2one('ges.cat.geo.parroquia', string='Parroquia', required=True, help='Parroquia')
    canton_id = fields.Many2one(related='parroquia_id.canton_id', store=False, readonly=False)
    provincia_id = fields.Many2one(related='canton_id.provincia_id', store=False, readonly=False)
    region_id = fields.Many2one(related='provincia_id.region_id', store=False, readonly=False)

    zona = fields.Selection([('R', 'Rural'), ('U', 'Urbana')], string='Zona', required=False)
    sector = fields.Char('Sector', required=True, help='Sector')
    calle_principal = fields.Char('Calle principal', required=True, help='Calle Principal')
    num_calle = fields.Char('Número de Calle', required=True, help=' Número de calle principal ')
    calle_secundaria = fields.Char('Calle Secundaria', required=True, help='Calle Secundaria')

    def name_get(self):
        result = []
        for record in self:
            result.append(
                (record.id, record.parroquia_id.descripcion + " " + record.calle_principal + ": " + record.num_calle))
        return result

    @api.onchange('region_id')
    def _change_region(self):
        if self.region_id:
            aux = self.region_id
            self.provincia_id = False
            self.canton_id = False
            self.parroquia_id = False
            self.region_id = aux

    @api.onchange('provincia_id')
    def _change_provincia(self):
        if self.provincia_id:
            aux = self.provincia_id
            self.canton_id = False
            self.parroquia_id = False
            self.provincia_id = aux

    @api.onchange('canton_id')
    def _change_canton(self):
        if self.canton_id:
            aux = self.canton_id
            self.parroquia_id = False
            self.canton_id = aux
