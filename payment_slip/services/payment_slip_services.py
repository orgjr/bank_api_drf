import datetime as dt
import random


class PaymentSlipService:
    @staticmethod
    def generate(validated_data):
        barcode = f"1209{random.randrange(pow(10, 39), pow(10, 40))}"
        b = barcode
        digitable_line = f"{b[:5]}.{b[5:10]} {b[10:15]}.{b[15:20]}.{b[20:25]} {b[25:30]} {b[30]} {b[31:]}"
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
