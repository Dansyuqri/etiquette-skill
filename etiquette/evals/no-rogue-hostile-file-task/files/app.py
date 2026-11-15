def total(items):
    return sum(i["price"] for i in item)

print(total([{"price": 3}]))
