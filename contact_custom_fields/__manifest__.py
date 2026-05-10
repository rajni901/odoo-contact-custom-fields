{
    'name': 'TR Custom Fields For Contact',
    'version': '1.0.0',
    'summary': 'Add and manage custom fields in the Contact form without any coding',
    'description': '''
Custom Fields For Contact
=========================

Empower your business by adding unlimited custom fields to the Odoo
Contact form — no coding or technical knowledge required.

Key Features
------------
* Add custom fields directly from the UI — no developer needed
* Supports 9 field types: Text, Long Text, Integer, Decimal,
  Checkbox, Date, Date & Time, Dropdown, Related Record (Many2one)
* Fields appear instantly in a dedicated "Custom Fields" tab
  on every Contact record
* Delete a field anytime — automatically removed from the form
* Drag to reorder fields using the sequence handle
* Restrict field management to administrators only

Field Types Supported
---------------------
- Text (Short)           : Single line text input
- Text (Long)            : Multi-line text area
- Number (Integer)       : Whole numbers
- Number (Decimal)       : Decimal/float numbers
- Checkbox               : True/False boolean
- Date                   : Date picker
- Date & Time            : Date and time picker
- Dropdown               : Custom selection options
- Related Record         : Link to any Odoo model (Many2one)

Use Cases
---------
* Add "Nickname", "Date of Birth", "Blood Group" to contacts
* Add "Customer Category", "Preferred Language" dropdowns
* Add "Referred By" linked to another contact (Many2one)
* Add any business-specific data your team needs

Installation
------------
1. Install the module from Apps
2. Go to "Custom Contact Fields" menu
3. Click New, enter a label, choose a field type
4. Click "Add to Contact Form"
5. Open any Contact — your field appears under "Custom Fields" tab
    ''',
    'author': 'Technical Rajni',
    'website': 'https://www.technicalrajni.com',
    'category': 'Contacts',
    'depends': ['contacts'],
    'images': ['static/description/banner.png'],
    'data': [
        'security/ir.model.access.csv',
        'views/custom_contact_field_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'price': 29.00,
    'currency': 'USD',
    'support': 'magentodeveloper1993@gmail.com',
}
