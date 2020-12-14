import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
}


# 스킨케어 - 쿠팡랭킹순 모든 상품,가격 가져오기


def product_by_link(url):
    result = requests.get(url, headers=headers)
    soup_obj = BeautifulSoup(result.content, "html.parser")

    productDiv = soup_obj.find("div", {"class": "prod-buy"})
    try:
        title = soup_obj.find("div", {"class": "prod-buy-header"}).find("h2",
                                                                        {
                                                                            "class": "prod-buy-header__title"}).text.strip()
    except Exception as ex:
        print(ex)
        title = ""
        pass
    try:
        product_image_img = soup_obj.find("div", {"class": "prod-image"}).find("div",
                                                                               {"class": "prod-image-container"}).find(
            "img",
            {"class": "prod-image__detail"})
        product_image = product_image_img['src'].replace("//", "")
    except Exception as ex:
        print(ex)
        product_image = ""
        pass

    try:
        price = soup_obj.find("div", {"class": "prod-sale-price"}).find("span", {"class": "total-price"}).text.strip()
    except Exception as ex:
        print(ex)
        price = 0
        pass

    try:

        shipping_info_title = soup_obj.find("div", {"class": "prod-shipping-fee"}). \
            find("div", {"class": "SHIPPING_FEE_DISPLAY_0"})
        if shipping_info_title:
            shipping_info_title = "무료배송"
        else:
            shipping_info_title = soup_obj.find("div", {"class": "prod-shipping-fee"}) \
                .find("em", {"class": "prod-txt-bold"}).text.strip()

    except Exception as ex:
        print(ex)
        shipping_info_title = ""
        pass

    try:
        shipping_info_values = soup_obj.find("div", {"class": "prod-pdd-container"}).findAll("em")
        shipping_info_value = ""
        if shipping_info_values:
            for shpinv in shipping_info_values:
                shipping_info_value += shpinv.text.strip()
        else:
            if shipping_info_title == "무료배송":
                shipping_info_value = 0
            else:
                shipping_info_value = "Not found"
    except Exception as ex:
        print(ex)
        shipping_info_value = ""
        pass

    price = int(''.join(filter(str.isdigit, price)))
    if price < 20000:
        service_fee = 2000
    elif 20000 < price < 50000:
        service_fee = price * 0.1
    elif 50000 < price < 70000:
        service_fee = price * 0.09
    elif 70000 < price < 100000:
        service_fee = price * 0.08
    elif 100000 < price < 150000:
        service_fee = price * 0.07
    elif 150000 < price < 200000:
        service_fee = price * 0.06
    else:
        service_fee = price * 0.05

    product = {
        'title': title,
        'image': product_image,
        'price': price,
        'service_fee': service_fee,
        'delivery_title': shipping_info_title,
        'delivery_fee': shipping_info_value,
        'url': url
    }
    return product
