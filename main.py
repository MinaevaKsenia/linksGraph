from urllib.parse import urlparse, urljoin
import random
from bs4 import BeautifulSoup
import requests
import networkx
import matplotlib.pyplot as plt


class LinksParser:
    """
    Класс-парсер ссылок со страниц.
    """
    def __init__(self):
        self.int_url = set()  # внутренние ссылки
        self.ext_url = set()  # внешние ссылки
        self.node_number = 0  # номер узла
        self.links_graph = networkx.Graph()  # граф
        self.node_list = {}  # список всех узлов
        self.old_node = ''  # старый родительский узел
        self.graph_depth = 0  # глубина графа
        self.max_depth = 0  # максимальная глубина

    def website_links(self, url, parent_node):
        """
        Метод, собирающий ссылки с поданной страницы.
        :param url: страница, с которой требуется собрать ссылки
        :param parent_node: узел родительской ссылки
        :return: словарь собранных ссылок с их узлами
        """
        urls = {}  # собранные на странице ссылки
        domain_name = urlparse(url).netloc  # извлечение доменного имени из URL
        soup = BeautifulSoup(requests.get(url).content, "html.parser")  # скачивание HTML страницы
        number_links = random.random() * 10  # задается количество узлов-детей
        self.links_graph.add_node(f'{self.node_number}')  # добавление родительского узла в граф

        for a_tag in soup.findAll("a"):
            number_links -= 1
            flag = False
            href = a_tag.attrs.get("href")
            if href == "" or href is None:  # href пустой тег
                continue
            href = urljoin(url, href)
            parsed_href = urlparse(href)
            # удалить параметры URL GET, фрагменты URL и т. д.
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path

            for passed_node, passed_link in self.node_list.items():
                # проверка связи ссылки с уже пройденными ссылками (устранение неуникальных ссылок)
                if passed_link == href:
                    if passed_node != parent_node:
                        self.links_graph.add_edge(passed_node, parent_node)
                    flag = True
            if flag:
                continue

            if domain_name not in href:
                if href not in self.ext_url:
                    print(f"[{self.node_number + 1}] Внешняя ссылка: {href}")
                    self.ext_url.add(href)
            else:
                print(f"[{self.node_number + 1}] Внутренняя ссылка: {href}")
                self.int_url.add(href)

            self.node_number += 1
            self.links_graph.add_node(f'{self.node_number}')
            self.links_graph.add_edge(parent_node, f'{self.node_number}')
            self.node_list[f'{self.node_number}'] = href
            urls[f'{self.node_number}'] = href
            if number_links <= 0:  # если собрали нужное количество ссылок
                break
        return urls

    # Просматриваем веб-страницу и извлекаем все ссылки.
    def crawl(self, url, parent_node, visit):
        """
        Метод перехода по собранным ссылкам.
        :param url: страница, с которой собираются ссылки
        :param parent_node: узел родительской ссылки
        :param visit: количество ссылок, которое нужно обойти
        """
        links = self.website_links(url, parent_node)
        if self.old_node != parent_node:  # проверка изменения глубины
            self.graph_depth += 1
            self.old_node = parent_node
        if self.graph_depth < self.max_depth:
            for received_node, received_link in links.items():
                if visit > 0:
                    self.crawl(received_link, received_node, 8)
                visit -= 1

    def get_depth(self):
        """
        Метод получения значения глубины с консоли.
        """
        depth_limit = 20
        print(f"Введите глубину графа. Значение должно быть не больше {depth_limit}.")
        self.max_depth = input()
        if not self.max_depth.isdigit() or int(self.max_depth) > depth_limit:
            print("Неверный ввод. Попробуйте снова.")
            self.get_depth()
        else:
            self.max_depth = int(self.max_depth)

    def get_start_link(self):
        """
        Метод получение начальной ссылки с консоли.
        :return: начальная ссылка
        """
        print("Введите ссылку:")
        received_start_link = input()
        if "http" not in received_start_link:
            print("Попробуйте снова.")
            received_start_link = self.get_start_link()
        return received_start_link

if __name__ == '__main__':
    links_parser = LinksParser()

    start_link = links_parser.get_start_link()  # получение начальной ссылки
    links_parser.get_depth()  # получение значения глубины
    links_parser.node_list['0'] = start_link
    links_parser.crawl(start_link, '0', 8)
    print("[+] Внешние ссылки:", len(links_parser.ext_url))
    print("[+] Внутренние ссылки:", len(links_parser.int_url))
    print("[+] Все ссылки:", len(links_parser.ext_url) + len(links_parser.int_url))

    color_map = []  # карта цветов для каждого узла
    for node, link in links_parser.node_list.items():
        if node == '0':
            color_map.append('green')
        elif link in links_parser.ext_url:
            color_map.append('yellow')
        else:
            color_map.append('blue')

    plt.plot(-1.1, -0.8, marker="o", markersize=10, markeredgecolor="green",
             markerfacecolor="green")
    plt.text(-1.02, -0.82, 'Начальная ссылка')
    plt.plot(-1.1, -0.9, marker="o", markersize=10, markeredgecolor="yellow",
             markerfacecolor="yellow")
    plt.text(-1.02, -0.92, 'Внешняя ссылка')
    plt.plot(-1.1, -1, marker="o", markersize=10, markeredgecolor="blue", markerfacecolor="blue")
    plt.text(-1.02, -1.02, 'Внутренняя ссылка')

    networkx.draw(links_parser.links_graph, node_color=color_map, node_size=300, with_labels=True)
    plt.show()

    # B = networkx.to_dict_of_lists(linksGraph) # !!!!
    # print(B)
