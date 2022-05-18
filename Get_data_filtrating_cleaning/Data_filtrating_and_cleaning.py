import pandas as pd

### FUNCTIONS ###

#  Filtrate and clean column "Office price"
def office_price_filtrating(df):
    df = df[df["Office price"] != "Coworking Spaces (250 desks available)"]
    df = df[df["Office price"] != "Coworking Spaces (10 desks available)"]

    df["Office price"] = df["Office price"].apply(
        lambda x: "No information" if str(x).split(" ")[0] == "Coworking" else x
    )

    df["Office price"] = df["Office price"].apply(
        lambda x: str(x).split("\n")[0].split(" ")[1][1:]
        if x != "No information"
        else x
    )

    df["Office price"] = df["Office price"].apply(lambda x: str(x).replace(",", ""))
    df["Office price"] = df["Office price"].apply(
        lambda x: int(x) if x.isnumeric() else "No information"
    )

    df = df[df["Office price"] != "No information"]

    return df


def cleaning_floor_column(df):

    df["Floor"] = df["Building Floor"].map(str) + " " + df["Min. Term"].map(str)

    df["Floor"] = df["Floor"].apply(
        lambda x: x
        if (str(x).split(" ")[0] == "Floor" or str(x).split(" ")[-2] == "Floor")
        else "No information"
    )

    df["Floor"] = df["Floor"].apply(
        lambda x: str(x).split(" ")[:2] if str(x).split(" ")[0] == "Floor" else x
    )
    df["Floor"] = df["Floor"].apply(
        lambda x: str(x).split(" ")[-2:] if str(x).split(" ")[-2] == "Floor" else x
    )

    df["Building Floor"] = df["Floor"]
    df.drop(labels=["Floor"], axis=1, inplace=True)

    df["Building Floor"] = df["Building Floor"].apply(
        lambda x: x if x[0] == "Floor" else "No information"
    )

    df["Building Floor"] = df["Building Floor"].apply(
        lambda x: x[1:] if x[0] == "Floor" else "No information"
    )

    df["Building Floor"] = df["Building Floor"].apply(
        lambda x: " ".join([str(elem) for elem in x])
    )
    df["Building Floor"] = df["Building Floor"].apply(
        lambda x: x if len(str(x)) <= 2 else "No information"
    )
    df["Building Floor"] = df["Building Floor"].apply(lambda x: x.replace(",", ""))

    return df


pd.set_option("display.max_rows", 50, "display.max_columns", 10)

df = pd.read_excel("./All_data_no_filtrated.xlsx")

df.drop(labels=["Unnamed: 0"], axis=1, inplace=True)
df.rename(columns={"People": "Up to [people]"}, inplace=True)

# CLEARING PRICE COLUMN
df = office_price_filtrating(df)


# CLEARING FLOOR COLUMN
df = cleaning_floor_column(df)


df["Min. Term"] = df["Min. Term"].apply(
    lambda x: str(x).split(" ")[2]
    if str(x).split(" ")[0] == "Min"
    else "No information"
)

df["Min. Term"] = df["Min. Term"].apply(
    lambda x: int(x[0])
    if str(x)[1] == "m"
    else int(x[0]) * 12
    if str(x)[1] == "y"
    else x
)
df.rename(columns={"Min. Term": "Min. Term [months]"}, inplace=True)

df["Area"] = df["Up to [people]"].apply(
    lambda x: "No information"
    if len(str(x).split("(")) == 1
    else (str(x).split("(")[1])[:-1]
)

df["Area"] = df["Area"].apply(
    lambda x: int(str(x).split(" ")[0]) if x != "No information" else x
)
df.rename(columns={"Area": "Area [sqft]"}, inplace=True)


df["Up to [people]"] = df["Up to [people]"].apply(lambda x: str(x).split("(")[0])
df["Up to [people]"] = df["Up to [people]"].apply(
    lambda x: x if len(str(x).split(" ")) < 3 else str(x).split(" ")[2]
)


df.replace("No information", "NUN", inplace=True)
df.to_excel("./Data_xlsx/Cleaned_data.xlsx", engine="xlsxwriter")
