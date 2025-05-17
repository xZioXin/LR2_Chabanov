import json
from datetime import datetime

DAY_RATE = 1.5
NIGHT_RATE = 0.9
ROLLOVER_DAY = 100
ROLLOVER_NIGHT = 80

DATA_FILE = globals().get("DATA_FILE", "counters_data.json")

class ElectricityCounter:
    def __init__(self):
        self.counters = self.load_data()
        self.history = []
    
    def load_data(self):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "counters": {},
                "bills": []
            }
    
    def save_data(self):
        with open(DATA_FILE, 'w') as f:
            json.dump({"counters": self.counters["counters"], "bills": self.counters["bills"]}, f, indent=2)
    
    def process_counter(self, counter_id, day_value, night_value, date=None):
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            day_value = float(day_value)
            night_value = float(night_value)
        except ValueError:
            raise ValueError("Невірний формат даних - значення мають бути числами")
        
        prev_data = self.counters["counters"].get(counter_id)
        
        if prev_data is None:
            self.counters["counters"][counter_id] = {
                "day": day_value,
                "night": night_value,
                "last_date": date
            }
            return {
                "status": "new_counter",
                "message": f"Додано новий лічильник {counter_id}",
                "counter_id": counter_id
            }
        
        prev_day = prev_data["day"]
        prev_night = prev_data["night"]
        rollover_applied = False
        
        day_used = day_value - prev_day
        night_used = night_value - prev_night
        
        if day_used < 0:
            rollover_applied = True
            day_used = (day_value + ROLLOVER_DAY) - prev_day
        if night_used < 0:
            rollover_applied = True
            night_used = (night_value + ROLLOVER_NIGHT) - prev_night
        
        day_cost = day_used * DAY_RATE
        night_cost = night_used * NIGHT_RATE
        total = day_cost + night_cost
        
        self.counters["counters"][counter_id] = {
            "day": day_value,
            "night": night_value,
            "last_date": date
        }
        
        bill = {
            "counter_id": counter_id,
            "date": date,
            "day_used": day_used,
            "night_used": night_used,
            "day_cost": round(day_cost, 2),
            "night_cost": round(night_cost, 2),
            "total": round(total, 2),
            "rollover_applied": rollover_applied
        }
        self.counters["bills"].append(bill)
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "action": "process_counter",
            "counter_id": counter_id,
            "data": bill
        })
        
        self.save_data()
        
        return {
            "status": "processed",
            "counter_id": counter_id,
            "bill": bill,
            "rollover_applied": rollover_applied
        }
    
    def get_counter_history(self, counter_id):
        return [bill for bill in self.counters["bills"] if bill["counter_id"] == counter_id]
    
    def get_all_bills(self):
        return self.counters["bills"]
    
    def get_processing_history(self):
        return self.history

if __name__ == "__main__":
    counter = ElectricityCounter()
    
    print("Двофазний лічильник 'день-ніч' - розрахунок вартості")
    print(f"Тарифи: день - {DAY_RATE} грн/кВт·год, ніч - {NIGHT_RATE} грн/кВт·год")
    
    while True:
        print("\nМеню:")
        print("1. Ввести показники лічильника")
        print("2. Переглянути історію лічильника")
        print("3. Вийти")
        
        choice = input("Виберіть опцію: ")
        
        if choice == "1":
            counter_id = input("Введіть ID лічильника: ")
            day_value = input("Введіть денні показники (кВт·год): ")
            night_value = input("Введіть нічні показники (кВт·год): ")
            date = input("Введіть дату (YYYY-MM-DD, залиште пустим для поточної дати): ") or None
            
            try:
                result = counter.process_counter(counter_id, day_value, night_value, date)
                print("\nРезультат обробки:")
                print(f"Лічильник: {result['counter_id']}")
                if result['status'] == "new_counter":
                    print("Додано новий лічильник")
                else:
                    bill = result['bill']
                    print(f"Дата: {bill['date']}")
                    print(f"Використано: день - {bill['day_used']} кВт·год, ніч - {bill['night_used']} кВт·год")
                    print(f"Вартість: день - {bill['day_cost']} грн, ніч - {bill['night_cost']} грн")
                    print(f"Загальна вартість: {bill['total']} грн")
                    if result['rollover_applied']:
                        print("УВАГА: Було застосовано накрутку через занижені показники!")
            except ValueError as e:
                print(f"Помилка: {e}")
        
        elif choice == "2":
            counter_id = input("Введіть ID лічильника для перегляду історії: ")
            history = counter.get_counter_history(counter_id)
            if not history:
                print("Історія для цього лічильника відсутня")
            else:
                print(f"\nІсторія лічильника {counter_id}:")
                for bill in history:
                    print(f"\nДата: {bill['date']}")
                    print(f"Використано: день - {bill['day_used']} кВт·год, ніч - {bill['night_used']} кВт·год")
                    print(f"Вартість: день - {bill['day_cost']} грн, ніч - {bill['night_cost']} грн")
                    print(f"Загальна вартість: {bill['total']} грн")
                    if bill.get('rollover_applied', False):
                        print("(Було застосовано накрутку)")
        
        elif choice == "3":
            print("Дякуємо за використання програми!")
            break
        
        else:
            print("Невірний вибір, спробуйте ще раз")