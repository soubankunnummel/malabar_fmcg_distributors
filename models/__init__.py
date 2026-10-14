# TODO Phase 2: product / lot / expiry extensions
# TODO Phase 3: purchase.order inherit (approval)
# TODO Phase 4: stock.picking / stock.quant inherit (FEFO, transfers)
# TODO Phase 5: sale.order + res.partner inherit (credit limit)
# TODO Phase 6: pos.session inherit (batch validation)
# TODO Phase 7: account.move inherit (reporting helpers)
from . import product_inherit
from . import purchase_inherit
from . import stock_inherit
from . import sale_inherit
from . import pos_inherit
from . import account_inherit
from . import res_partner_inherit
