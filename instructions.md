
# A complete beginners guide to The BuzzBot 

## Welcome, Traveler!

Welcome, Traveler! My name is Callum Alexander and welcome to The BuzzBot, a complete 
system for assigning club umpires to fixtures at Edinburgh University Men's Hockey Club. 
If you are reading this then you are likely a member of the committee, highly likely in 
the role of fixtures, umpiring, President, Vice President, or Secretary.



## RTFM

<div style="background-color: #ffcccc; color: #990000; padding: 10px; border-radius: 5px;">
<b>RTFM</b>. It stands for "Read the f*cking manual". 
</div>


Read this entire file in the order given, before you go about using the system because 
it is likely that you will get something wrong if you don't.

## The included files

There are four files included with The BuzzBot program - an input file for fixtures, a
configuration file, a locations file, and a time travel data file. All of them are required
for the program to function to **don't** delete any of them. When in doubt, don't edit any
*except* `input.csv`.

### `buzzbot.exe` / `buzzbot.app` - the main event

### `input.csv` - where you put the fixtures details

#### What is a `.csv` file anyway?

This is a fantastic question and if you are not on a STE(M) degree, you are unlikely to have encountered 
a file like this before. A __CSV file__, which stands for _"Comma-Separated Values_", is a type 
of file used to store tabular data in a simple plain-text format. Imagine it like a table 
you might see in Micros*ft Excel or Google Sheets, but instead of being stored in the confusing format
that Google or Micros\*ft offer which can only be opened by Excel or Google Sheets, 
it's just plain text that can be easily read and edited by both humans and computers, opened
with just about any text editing program.

Here's a basic breakdown of how CSV files work:

1. **Structure**: A CSV file typically consists of rows and columns, just like a spreadsheet. 
Each row represents a separate entry, and each column represents a different attribute or 
piece of information about that entry - just like an Excel or Google Sheets spreadsheet.

2. **Delimiter**: CSV files use a delimiter to separate the values in each row. The most 
common delimiter is a comma, but other characters like semicolons or tabs can also be used. 
Hence, the name "Comma-Separated Values". For the purpose of this program, we just stick with commas.

3. **Text Format**: CSV files are plain text files, which means they can be opened and edited
with any text editor, such as Notepad on Windows or TextEdit on Mac (**NOT Micros*ft Word or 
Apple Pages**). This simplicity makes them very portable and easy to work with. Because they
represent tabular data, they can be opened by Excel, Apple Numbers, Google Sheets too, but be careful that
when you are saving them after opening it in these programs that it is still saved as a 
`.csv` file and not as a `.xls` or `.xlt` or anything else. If you are using a MAC or a Windows computer, your computer
might try to open a `.csv` file in Excel or Numbers. I am not sure about Numbers, but Excel will do it automatically.

4. **Common Usage**: CSV files are widely used for various purposes, such as exporting data 
from databases, exchanging data between different programs or systems, and performing data 
analysis in tools like Excel or Python. They're especially popular for tasks involving large 
datasets due to their simplicity and efficiency.

For example, a CSV file representing a simple list of people might look like this:

```
Name, Age, City
John, 25, New York
Emily, 30, Los Angeles
Michael, 28, Chicago
```

Each row represents a person, with their name, age, and city listed in separate columns,
and commas separating the values within each row. From this example, you can see the similarity 
to spreadsheet applications such as Microsoft Excel or Google Sheets.

In summary, a CSV file is a text-based file format used for storing tabular data in a simple, 
easy-to-read format that can be easily manipulated and interpreted by computers and software 
applications.

#### Why not use Microsoft Excel or Google Sheets?


### `configuration.yaml` - configuration

### `locations.csv` - match day locations

### `distance_matrix_cache.json` - super important, don't delete

## How to use

## The user interface

## Adding new locations

## Input file format

## The configuration file

### First of all, what is a **variable**?

A variable is like a box that contains a value. The variable name is what you call the box
and represents the value of the thing inside a box. Think back to high school maths when
it suddenly started including letters as well as numbers, and you were using `x`'s and `y`'s.
They are mathematical variables. They have the names `x` and `y` and are used to represent
a value that can change or isn't defined yet. This is where the name 'variable' comes
from - the value of it varys or can change.

Everything in this configuration file is a variable, similar to mathematical variables.
It has a name (which is the variable name) and it has a value that you can change. 

When the program is run, it reads all the variable names and value in this file, and uses
them in the operation of the program. Changing these variables changes the way the program
runs.

### DistanceMatrix.AI

As part of the program's logic, the travel time between the locations of two matches
is required. In order to do this, the program automatically connects to a website
called [DistanceMatrix.AI](http://www.distancematrix.ai). This website does all the
heavily lifting for computing the travel time between two geographical points - kind 
of like the way Google Maps gives you an estimated travel time. 

Included with the Head of Umpiring handover document should be the club's login details and 
**API key** for the website. Think of an **API key** as a type of password. It is 
randomly generated by the website for your use and your use only, so don't go sharing it.
Whenever The BuzzBot 'talks' to this website, it uses the API provided in the config
to let the website know who is talking to it. It's kind of like a username and password
combined.

Included in the configuration file is are two lines, the first one indented by two spaces
and the second indented by four spaces:

```yaml
  distance_matrix_ai:
    api_key: "API KEY HERE"
```
To fill in the API key, remove the text API KEY HERE from inside the double quotes, and 
replace it with the club account API key mentioned above. See an example of what it
should look like with an example API key below:

```yaml
  distance_matrix_ai:
    api_key: "3j45k3k4j5l3-34k5jl345jlk43-5kl45jlk34j5-kl45jl3k4"
```
> **NOTE:**<br>
> Make sure that the first line (`distance_matrix_ai:`) is indented by **2** spaces
> from the start of the line, and the following line (`api_key: "...`) is indented 
> by **4** spaces from the start of the line.

### `taglines`

The `taglines` variable is used to store all the phrases that The BuzzBot can say at the 
top of the user interface. You are welcome to add and remove any that you wish.

> **NOTE:**<br>
> If you wish to add a phrase - on a new line, indent by **2** spaces from the start of
> the line, followed by a `-` and then the phrase that you wish to add. See below for an
> example:
> ```yaml 
> - This is an example of a phrase that The BuzzBot can say
> ```
> Notice the two spaces before the dash.

If you wish to remove a phrase, delete the entire line.


## Heuristics and assignment criteria 
