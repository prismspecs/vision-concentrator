text = "Ein Welpe rennt durch ein Feld"

from googletrans import Translator  
translator = Translator()
translation = translator.translate("Der Himmel ist blau und ich mag Bananen", dest='en')
print(translation.text)