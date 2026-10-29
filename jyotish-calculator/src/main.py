from datetime import date

from src.astronomy import sunrise_sunset


def main():
    day = date.today()
    events = sunrise_sunset(day)

    print("Jyotish Calculator")
    print("==================")
    print(f"Location: Harda, Madhya Pradesh")
    print(f"Date: {day.isoformat()}")
    print(f"Sunrise: {events['sunrise']:%I:%M:%S %p %Z}")
    print(f"Sunset:  {events['sunset']:%I:%M:%S %p %Z}")


if __name__ == "__main__":
    main()