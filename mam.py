import sys

import yadisk

y = yadisk.YaDisk("00428739321c477b84e4ac1286c07fda", "a14bcff18e9e402ba8b5e002275fc4fb", "AQAAAAAYv8QtAATVE8obRYC7RECrof_n5kF_lHw")
url = y.get_code_url()

print("Go to the following url: %s" % url)
code = input("Enter the confirmation code: ")

try:
    response = y.get_token(code)
except yadisk.exceptions.BadRequestError:
    print("Bad code")
    sys.exit(1)

y.token = response.access_token
print(response)
if y.check_token():
    print("Sucessfully received token!")
else:
    print("Something went wrong. Not sure how though...")
