import datetime as dt
import random


class PaymentSlipService:
    @staticmethod
    def generate(validated_data):
        barcode = f"1209{random.randrange(pow(10, 39), pow(10, 40))}"
        digitable_line = f"{a[:5]}.{a[5:10]} {a[10:15]}.{a[15:20]}.{a[20:25]} {a[25:30]} {a[30]} {a[31:]}"
        our_number = str(random.randrange(pow(9, 10)))
        document_number = str(
            f"{dt.datetime.now().strftime('%Y%m%d')}{random.randrange(pow(10, 3), pow(10, 4))}"
        )
        due_date = dt.date.today() + dt.timedelta(days=3)

        return {
            **validated_data,
            "barcode": barcode,
            "digitable_line": digitable_line,
            "our_number": our_number,
            "document_number": document_number,
            "due_date": due_date,
        }
