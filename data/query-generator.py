import csv

#IMPORTANT!!! Don't use this if you didn't write it :)

# Open the CSV file
with open('data/current_sections.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter='\n', quotechar='"')

    # Iterate through each row in the file and print its contents
    for row in reader:
        split = ', '.join(row).split(",")
        print('INSERT INTO classes VALUES (' + 
                                                split[0] + "," +
                                                "'" + split[1] + "'," +
                                                "'" + split[2] + "'," +
                                                split[3] + "," +
                                                split[4] + "," +
                                                "'" + split[5] + "'," +
                                                split[6] + ');')