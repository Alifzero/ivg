from odoo import models, api, fields, _ 


class CRMLeadLine(models.Model):
    _name = 'crm.lead.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _descript = 'CRM Lead Lines'


    name = fields.Char("Description", required=True, translate=True, tracking=True)
    lead_id = fields.Many2one("crm.lead", string="Lead")
    product_id = fields.Many2one("product.product", 
            string="Product", index=True, tracking=True)
    category_id = fields.Many2one("product.category", 
            string="Product Category", index=True, tracking=True)
    product_tmpl_id = fields.Many2one("product.template", 
            string="Product Template", index=True, tracking=True)
    product_barcode = fields.Char(string="Barcode",
            related="product_id.barcode",
            store=True)
    
    product_qty = fields.Integer(string="Product Quantity", 
            default=1, required=True, tracking=True)
    uom_id = fields.Many2one("uom.uom", 
            string="Unit of Measure", readonly=True, tracking=True)
    price_unit = fields.Float(string="Price Unit", tracking=True)
    
    company_id = fields.Many2one(related='lead_id.company_id')
    partner_id = fields.Many2one('res.partner',related="lead_id.partner_id")
    user_id = fields.Many2one(related="lead_id.user_id")

    #----------------------------------------------------
    # Onchange api
    #----------------------------------------------------

    @api.onchange("product_id")
    def _onchange_product_id(self):
        domain = {}
        if not self.lead_id:
            return

        if not self.product_id:
            self.price_unit = 0.0
            domain["uom_id"] = []
            if self.name and self.name != self.category_id.name:
                self.name = ""
        else:
            product = self.product_id
            self.category_id = product.categ_id.id
            self.product_tmpl_id = product.product_tmpl_id.id
            self.price_unit = product.list_price

            if product.name:
                self.name = product.name

            if (
                not self.uom_id
                or product.uom_id.category_id.id != self.uom_id.category_id.id
            ):
                self.uom_id = product.uom_id.id
            
            domain["uom_id"] = [("category_id", "=", product.uom_id.category_id.id)]

            if self.uom_id and self.uom_id.id != product.uom_id.id:
                self.price_unit = product.uom_id._compute_price(
                    self.price_unit, self.uom_id
                )
        return {"domain": domain}

    @api.onchange("category_id")
    def _onchange_category_id(self):
        domain = {}
        if not self.lead_id:
            return
        
        if self.category_id:
            categ_id = self.category_id
            if categ_id.name and not self.name:
                self.name = categ_id.name

            # Check if there are already defined product and product template
            # and remove them if categories do not match
            if self.product_id and self.product_id.categ_id != categ_id:
                self.product_id = None
                self.name = categ_id.name
            if self.product_tmpl_id and self.product_tmpl_id.categ_id != categ_id:
                self.product_tmpl_id = None

        return {"domain": domain}

    @api.onchange("product_tmpl_id")
    def _onchange_product_tmpl_id(self):
        domain = {}
        if not self.lead_id:
            return
        if self.product_tmpl_id:
            product_tmpl = self.product_tmpl_id
            if product_tmpl.name and not self.name:
                self.name = product_tmpl.name
            self.category_id = product_tmpl.categ_id

            if self.product_id:
                # Check if there are already defined product and remove
                # if it does not match
                if self.product_id.product_tmpl_id != product_tmpl:
                    self.product_id = None
                    self.name = product_tmpl.name

        return {"domain": domain}

    @api.onchange("uom_id")
    def _onchange_uom_id(self):
        result = {}
        if not self.uom_id:
            self.price_unit = 0.0

        if self.product_id and self.uom_id:
            price_unit = self.product_id.list_price
            self.price_unit = self.product_id.uom_id._compute_price(
                price_unit, self.uom_id
            )
        return result
