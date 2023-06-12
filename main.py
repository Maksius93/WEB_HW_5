import platform
import aiohttp
import asyncio
from datetime import datetime, timedelta
import sys


class ExchangeRateAPI:
    async def get_exchange_rates(self, session, date):
        url = f"https://api.privatbank.ua/p24api/exchange_rates?json&date={date.strftime('%d.%m.%Y')}"

        async with session.get(url) as response:
            if response.status != 200:
                return None

            result = await response.json()
            return result


class ExchangeRateParser:
    def parse_exchange_rates(self, rates, additional_currencies):
        currencies = rates['exchangeRate']
        parsed_rates = []

        for currency in currencies:
            if currency['currency'] in additional_currencies:
                rate = {
                    currency['currency']: {
                        'sale': float(currency['saleRateNB']),
                        'purchase': float(currency['purchaseRateNB'])
                    }
                }
                parsed_rates.append({rates['date']: rate})

        return parsed_rates


class ExchangeRatePrinter:
    def print_exchange_rates(self, output_rates):
        for date, currencies in output_rates.items():
            print(date)
            for currency, rate in currencies.items():
                print(currency, rate)
            print()


class CurrencyExchangeApp:
    def __init__(self, num_days, additional_currencies):
        self.num_days = num_days
        self.additional_currencies = additional_currencies
        self.today = datetime.today()
        self.start_date = self.today - timedelta(days=num_days)
        self.dates = [self.start_date + timedelta(days=i) for i in range(num_days)]

        self.api = ExchangeRateAPI()
        self.parser = ExchangeRateParser()
        self.printer = ExchangeRatePrinter()

    async def fetch_exchange_rates(self, session, date):
        return await self.api.get_exchange_rates(session, date)

    def process_exchange_rates(self, exchange_rates):
        parsed_rates = []
        for rates in exchange_rates:
            if rates is not None:
                parsed_rates.extend(self.parser.parse_exchange_rates(rates, self.additional_currencies))
        return parsed_rates

    def format_output_rates(self, parsed_rates):
        output_rates = {}
        for rate in parsed_rates:
            date = list(rate.keys())[0]
            currency = list(rate[date].keys())[0]
            if date not in output_rates:
                output_rates[date] = {}
            output_rates[date][currency] = rate[date][currency]
        return output_rates

    async def main(self):
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_exchange_rates(session, date) for date in self.dates]
            exchange_rates = await asyncio.gather(*tasks)
            parsed_rates = self.process_exchange_rates(exchange_rates)
            output_rates = self.format_output_rates(parsed_rates)
            self.printer.print_exchange_rates(output_rates)

    def run(self):
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(self.main())


if __name__ == "__main__":
    try:
        num_days = int(sys.argv[1]) if len(sys.argv) > 1 else 10
        additional_currencies = sys.argv[2:] if len(sys.argv) > 2 else []
        app = CurrencyExchangeApp(num_days, additional_currencies)
        app.run()
    except Exception as e:
        print(f"An error occurred: {str(e)}")






