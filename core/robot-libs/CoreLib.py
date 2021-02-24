import json

from robot.api.deco import keyword
from playwright.sync_api import sync_playwright

from utils import write_results

class CoreLib(object):
  @keyword('Abrir o navegador em')
  def open_browser(self, url, headless = True, slow_mo: float = None):
    self.playwright = sync_playwright().start()
    self.browser = self.playwright.firefox.launch(headless=headless, slow_mo=slow_mo)
    self.page = self.browser.new_page()
    self.page.goto(url)

  @keyword('Clicar em')
  def click_at(self, selector):
    self.page.click(selector)

  @keyword('Digitar texto em campo')
  def input_text(self, text: str, selector):
    self.page.fill(selector, text)

  @keyword('Esperar até que elemento esteja visivel')
  def wait_for_element(self, selector):
    self.page.wait_for_selector(selector)

  @keyword('Pegar dados da tabela em JSON')
  def dump_table(self, selector, header_at = 1, data_begins_at = 2):
    table_data: list[dict] = []
    raw_data = self.page.query_selector(selector).inner_text().split('\n')
    headers = raw_data[header_at - 1].split('\t')

    raw_data = raw_data[(data_begins_at - 1):]
    for str_data in raw_data:
      arr_data = str_data.split('\t')
      table_data.append(dict(zip(headers, arr_data)))

    write_results(json.dumps(table_data, ensure_ascii=False))

  @keyword('Fechar navegador e parar playwright')
  def teardown(self):
    self.page.close()
    self.browser.close()
    self.playwright.stop()
