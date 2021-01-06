import datetime

default_shop_config = {
    'telegram_store': '',
    'telegram_new_order': '',
    'telegram_accept': '',
    'sms_enabled': False,
    'app_enabled': False
}


def getNewOrderNumber(orderId):
    today = datetime.date.today()
    year = u'%4s' % today.year
    month = u'%02i' % today.month
    day = u'%02i' % today.day

    return '{}-{}-{}-{}'.format(year, month, day, orderId)


def getInvoiceNumber(month, invoiceId):
    if invoiceId < 10:
        return '{}-000{}'.format(month, invoiceId)
    elif invoiceId < 100:
        return '{}-00{}'.format(month, invoiceId)
    elif invoiceId < 1000:
        return '{}-0{}'.format(month, invoiceId)
    else:
        return '{}-{}'.format(month, invoiceId)
