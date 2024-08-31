import pandas as pd
import string
import nltk
import re
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import words

nltk.download('words')
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')


def text_columns_process(ec_df, text_columns):
    # Turn all the words to lowercase
    for col in text_columns:
        ec_df['{}_lowercase'.format(col)] = ec_df[col].str.lower()

    # ## Remove whitespace
    for col in text_columns:
        ec_df['{}_strip'.format(col)] = ec_df['{}_lowercase'.format(col)].str.strip()

    # ## Remove special characters and puncutation
    for col in text_columns:
        text = ec_df['{}_strip'.format(col)].str.replace('[^\w]', ' ', regex=True)
        remove_punc = dict((ord(char), None) for char in string.punctuation)
        ec_df['{}_cleaned'.format(col)] = text.str.translate(remove_punc)

    # ## Strip accents
    for col in text_columns:
        text_col = ec_df['{}_cleaned'.format(col)]
        # ec_df['{}_cleaned'.format(col)] = text_col.apply(lambda x: unidecode(str(x)))
        ec_df['{}_cleaned'.format(col)] = ec_df['{}_cleaned'.format(col)].str.strip()

    return ec_df


def tokenize_and_lemmatize(df):
    wl = WordNetLemmatizer()
    _non_word_match = re.compile(r'[^\w]+')
    _run_of_digits = re.compile(r'\d+')
    stopws = set(stopwords.words('english'))

    def toki(text):
        return [word for sent in sent_tokenize(text)
                for word in word_tokenize(sent) if word not in stopws]

    tokens = df['eligibilityCriteria_cleaned'].apply(lambda x: toki(x))
    df['ec_cleaned_tokenized'] = tokens

    token_length_min = 1
    token_length_max = 20

    filtered_tokens = [[token for token in sublist if token_length_min < len(token) <= token_length_max] for sublist in
                       tokens]

    lemmatizer = WordNetLemmatizer()
    lemmatized_words = [[lemmatizer.lemmatize(token) for token in sublist] for sublist in filtered_tokens]

    lemmatized_words_nonu = [[le for le in sublist if not le.isdigit()] for sublist in lemmatized_words]

    lemmatized_words_eng = [[word for word in sublist if word in words.words()] for sublist in lemmatized_words_nonu]
    df['ec_lemmatized_eng'] = lemmatized_words_eng

    processed_text = [' '.join(lemmatized_word for lemmatized_word in sublist) for sublist in lemmatized_words_nonu]
    df['ec_processed_text'] = processed_text

    return df


def main(file_location_path: str, lemma=False):
    df = pd.read_csv(file_location_path)

    # clean text columns
    df = text_columns_process(df, text_columns=["eligibilityCriteria", "studyPopulation"])

    columns_to_keep = [col for col in df.columns if '_cleaned' in col] + ["nctId", "healthyVolunteers",
                                                                          "sex", "genderBased", "minimumAge",
                                                                          "maximumAge", "stdAges"]
    columns_with_mv = df[columns_to_keep].columns[df[columns_to_keep].isnull().any()]
    # check the number of missing values of each column
    print('Columns with missing values and count:', df[columns_with_mv].isnull().sum().sort_values())

    # Columns
    # with missing values and count:
    # healthyVolunteers
    # 1
    # minimumAge
    # 2
    # maximumAge
    # 4
    # studyPopulation_cleaned
    # 15
    # genderBased
    # 27
    # dtype: int64

    #  remove duplicated values
    # df = df.drop_duplicates(subset=columns_to_keep

    # if should execute tokenize_and_lemmatize
    # don't have as much experience with NER, not sure if it helps
    if lemma:
        df = tokenize_and_lemmatize(df)

    # lean up columns and save cleaned file
    for col in df.columns:
        try:
            df.drop(['{}_lowercase'.format(col)], axis=1, inplace=True)
            df.drop(['{}_strip'.format(col)], axis=1, inplace=True)
            if col not in columns_to_keep:
                df.drop([col], axis=1, inplace=True)
        except:
            continue

    df.to_csv("{}-cleaned.csv".format(file_location_path.strip('.csv')), index=False)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("file_location_path", type=str, help="file location of the csv")
    parser.add_argument("--lemma", action='store_true', help="should the script lemmatize text")

    args = parser.parse_args()
    file_location_path = args.file_location_path
    main(file_location_path)
