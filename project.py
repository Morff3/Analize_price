import os
import csv

class PriceMachine:
    def __init__(self):

        self.data = []
        self.product_names = {"название", "продукт", "товар", "наименование"}
        self.price_names = {"цена", "розница"}
        self.weight_names = {"фасовка", "масса", "вес"}

    def load_prices(self, directory='.', delimiter=','):

        try:
            files = os.listdir(directory)
        except FileNotFoundError:
            print(f"Директория '{directory}' не найдена.")
            return

        price_files = [file for file in files if 'price' in file.lower() and file.lower().endswith('.csv')]

        if not price_files:
            print("Файлы с прайс-листами не найдены в директории.")
            return

        for file in price_files:
            file_path = os.path.join(directory, file)
            try:
                with open(file_path, encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile, delimiter=delimiter)
                    headers = next(reader, None)
                    if headers is None:
                        print(f"Файл '{file}' пустой.")
                        continue

                    col_indices = self._search_product_price_weight(headers)
                    if not col_indices:
                        print(f"Не найдены необходимые столбцы в файле '{file}'. Пропуск файла.")
                        continue

                    product_idx, price_idx, weight_idx = col_indices

                    for row_number, row in enumerate(reader, start=2):
                        try:
                            product = row[product_idx].strip()
                            price = float(row[price_idx].replace(',', '.'))
                            weight = float(row[weight_idx].replace(',', '.'))

                            if weight == 0:
                                print(f"Вес равен нулю в файле '{file}', строка {row_number}. Пропуск записи.")
                                continue

                            price_per_kg = price / weight

                            self.data.append({
                                "product": product,
                                "price": price,
                                "weight": weight,
                                "price_per_kg": price_per_kg,
                                "file": file
                            })
                        except IndexError:
                            print(f"Недостаточно данных в файле '{file}', строка {row_number}. Пропуск записи.")
                        except ValueError:
                            print(f"Некорректные данные в файле '{file}', строка {row_number}. Пропуск записи.")
            except Exception as e:
                print(f"Не удалось прочитать файл '{file}': {e}")

        print(f"Загружено {len(self.data)} товаров из {len(price_files)} файлов.")

    def _search_product_price_weight(self, headers):

        product_idx = price_idx = weight_idx = None
        headers_lower = [header.strip().lower() for header in headers]

        for idx, header in enumerate(headers_lower):
            if header in self.product_names and product_idx is None:
                product_idx = idx
            elif header in self.price_names and price_idx is None:
                price_idx = idx
            elif header in self.weight_names and weight_idx is None:
                weight_idx = idx


        if product_idx is not None and price_idx is not None and weight_idx is not None:
            return (product_idx, price_idx, weight_idx)
        else:
            return None

    def export_to_html(self, fname='output.html', entries=None):

        if entries is None:
            entries = self.data

        html_content = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Позиции продуктов</title>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:hover {background-color: #f5f5f5;}
    </style>
</head>
<body>
    <h2>Позиции продуктов</h2>
    <table>
        <tr>
            <th>№</th>
            <th>Наименование</th>
            <th>Цена (руб.)</th>
            <th>Вес (кг)</th>
            <th>Файл</th>
            <th>Цена за кг. (руб.)</th>
        </tr>
'''
        for idx, entry in enumerate(entries, start=1):
            html_content += f'''
        <tr>
            <td>{idx}</td>
            <td>{entry["product"]}</td>
            <td>{entry["price"]}</td>
            <td>{entry["weight"]}</td>
            <td>{entry["file"]}</td>
            <td>{entry["price_per_kg"]:.2f}</td>
        </tr>
'''
        html_content += '''
    </table>
</body>
</html>
'''
        try:
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"Данные успешно экспортированы в '{fname}'.")
        except Exception as e:
            print(f"Не удалось записать HTML-файл '{fname}': {e}")

    def find_text(self, text):
        text_lower = text.lower()
        matching = [entry for entry in self.data if text_lower in entry["product"].lower()]
        sorted_matching = sorted(matching, key=lambda x: x["price_per_kg"])
        return sorted_matching

def main():

    pm = PriceMachine()
    directory = '.'
    delimiter = ','
    pm.load_prices(directory, delimiter=delimiter)

    while True:
        user_input = input("Введите текст для поиска (или 'exit' для выхода): ").strip()
        if user_input.lower() == 'exit':
            print("Работа завершена.")
            break
        elif user_input == '':
            print("Пожалуйста, введите непустой текст для поиска.")
            continue
        else:
            results = pm.find_text(user_input)
            if not results:
                print("Ничего не найдено.")
            else:
                print(f"\nНайдено {len(results)} позиций:")
                print("{:<5} {:<40} {:<10} {:<10} {:<20} {:<15}".format(
                    "№", "Наименование", "Цена", "Вес", "Файл", "Цена за кг."
                ))
                print("-" * 100)
                for idx, entry in enumerate(results, start=1):
                    product_display = (entry["product"][:37] + '...') if len(entry["product"]) > 40 else entry["product"]
                    print("{:<5} {:<40} {:<10} {:<10} {:<20} {:<15.2f}".format(
                        idx,
                        product_display,
                        entry["price"],
                        entry["weight"],
                        entry["file"],
                        entry["price_per_kg"]
                    ))
                while True:
                    export = input("Экспортировать результаты в HTML? (y/n): ").strip().lower()
                    if export == 'y':
                        sanitized_input = "_".join(user_input.split())
                        html_filename = f"search_results_{sanitized_input}.html"
                        pm.export_to_html(fname=html_filename, entries=results)
                        break
                    elif export == 'n':
                        break
                    else:
                        print("Пожалуйста, введите 'y' или 'n'.")

    while True:
        export_all = input("Экспортировать все данные в HTML? (y/n): ").strip().lower()
        if export_all == 'y':
            pm.export_to_html()
            break
        elif export_all == 'n':
            break
        else:
            print("Пожалуйста, введите 'y' или 'n'.")

if __name__ == "__main__":
    main()
