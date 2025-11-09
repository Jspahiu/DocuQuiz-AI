from chatbot import *
from pdf_creater import *
from pdf_loader import *
from config import *


class DocuQuizAI:
    def __init__(self, pdf_files:list, reset_vectorstore:bool=True):
        # Don't create the Chatbot until we have a token_count from the PDF loader
        self.pdf_files = pdf_files
        self.reset_vectorstore = reset_vectorstore
        self.bot = None
        self.token_count = None

    def quiz_creater(self, token_count):
        query = "Make me a quiz based on the document." 
        response = self.bot.query(query, token_count)
        print("Answer:", response)
        return response
    
    def pdf_loader(self):
        pdf_loader_class = PDFLoader(
            pdf_path=r"images\test.png",
            tesseract_path=r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            output_pdf_path=r"data_sets\document.pdf"
        )
        pic_or_not = input("Is your file an image? (y/n/exit): ")

        if pic_or_not.lower() == 'y':
            pass

        elif pic_or_not.lower() == 'n':
            text, token_count = pdf_loader_class.extract_text_tesseract()
            pdf_loader_class.text_to_pdf(text)
            return text, token_count

        elif pic_or_not.lower() == 'exit':
            exit()

    def pdf_creater(self, text_use):
        pdf_creator = PDFCreator(
            output_pdf_path=r"docuquiz_results/docuquiz_quiz.pdf.pdf",
            logo_path=r"logo\docuquiz_logo_transparent.png",
            text=text_use,
        )
        pdf_creator.create_pdf_with_unicode_text()
    
    def main(self):
        self.quiz_creater()

if __name__ == "__main__":
    # Create app (do not create Chatbot yet)
    app = DocuQuizAI(pdf_files=[r"data_sets\document.pdf"], reset_vectorstore=True)

    # Load the PDF (or image), convert to PDF and get text + token count
    result = app.pdf_loader()
    if result is None:
        print("No document loaded. Exiting.")
        exit()
    text_content, tokens_count = result

    # Create Chatbot now that we have the token count
    app.bot = Chatbot(app.pdf_files, app.reset_vectorstore, tokens_count)
    app.bot.initialize()

    # Generate quiz using the actual token count
    quiz_text = app.quiz_creater(tokens_count)
    app.pdf_creater(quiz_text)