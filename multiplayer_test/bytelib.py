import pickle

# Исходный словарь
my_dict = {'key1': 'value1', 'key2': 42, 'key3': [1, 2, 3]}

# Преобразуем словарь в байты
dict_as_bytes = pickle.dumps(my_dict)
print("Словарь в виде байтов:")
print(dict_as_bytes)

# Преобразуем байты обратно в словарь
bytes_as_dict = pickle.loads(dict_as_bytes)
print("\nБайты преобразованы обратно в словарь:")
print(bytes_as_dict)

# Проверяем, что исходный словарь и полученный после преобразования совпадают
print("\nСовпадают ли исходный словарь и восстановленный?")
print(my_dict == bytes_as_dict)