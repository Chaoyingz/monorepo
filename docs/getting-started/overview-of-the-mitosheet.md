---
description: >-
  A basic page that introduces you to the high-level concepts helpful in
  understanding how the Mitosheet works.
---

# Overview of the Mitosheet

### The Mitosheet in a notebook

Mitosheet is simply a spreadsheet that exists inside of your Jupyter notebook. This allows you to _very_ quickly bounce back and forth between doing data analysis in Python and exploring/manipulating your data in the Mitosheet.

Because the Mitosheet is optimized for your Python data analysis, every tab inside of your Mitosheet represents a Pandas dataframe. To demonstrate this dataframe aspect, let's take a look at displaying a single dataframe (of Tesla stock prices) in a Mitosheet:

![](<../.gitbook/assets/Screen Shot 2022-02-17 at 2.26.18 PM.png>)

Note that the Mitosheet can also help you easily import your CSV and Excel files into dataframes with just the click of a button. You can see more about [importing data into Mito.](../how-to/importing-data-to-mito.md)

### Exploring your data in the Mitosheet

Once we've got a dataframe displayed in the Mitosheet, we can immediately begin to explore our data like we were in a standard spreadsheet. Let's highlight a few ways to use the Mitosheet to explore your dataset.

#### Immediately visible data

![.](<../.gitbook/assets/Screen Shot 2022-02-17 at 2.26.18 PM copy.png>)

Unlike just printing out a dataframe, Mito immediately allows you to see your entire data set. As you can see from the above screenshot, Mito makes it incredibly easy to:

1. See the column headers of your dataframe.
2. Scroll through the rows of your dataframe and look for data points of interest.
3. View the types of each of the columns in your dataframe.
4. See the number of rows and colums in your dataframe.

There are a variety of more advanced ways to explore and understand your data, easily allowing you to access [column summary statistics](../how-to/summary-statistics.md), [graph your data](../how-to/graphing.md), and [more.](../how-to/pivot-tables.md)

### Editing your data in the Mitosheet

On top of just allowing you to explore your data in a spreadsheet, the Mitosheet allows you to easily edit your data. You can find most of the basic actions in the toolbar at the top of the Mitosheet.

Included actions allow you to edit columns in your dataframe, create [pivot tables](../how-to/pivot-tables.md), [merge multiple dataframes together](../how-to/merging-datasets-together.md), and much more.

![](<../.gitbook/assets/Screen Shot 2022-02-17 at 2.26.18 PM copy 2.png>)

Furthermore, you can use the Action Search bar to search for any functionality that is included in the Mitosheet. If you're not sure how to find some functionality in the Mitosheet, try searching for it!

#### Editing columns in the sheet

One of the most basic operations you may perform in any spreadsheet is adding a column, and writing a spreadsheet formula. Let's use the Mitosheet to calculate the Tesla stock price movement over each trading day.

1. First, use the add column button to add a column to the dataset.
2. Then, double click on the column header to edit it directly and rename it to `Movement.`

![](<../.gitbook/assets/Screen Shot 2022-02-17 at 3.05.05 PM.png>)

Now that we have a new column, we can write a formula inside of it! Simply:

1. Double click on a cell in the column
2. Set the formula, referencing the other column headers by their name.

![](<../.gitbook/assets/Screen Shot 2022-02-17 at 3.05.36 PM.png>)

After pressing enter, we can see we've easily calculated a new column in our dataframe, just like we would in a spreadsheet.

![](<../.gitbook/assets/Screen Shot 2022-02-17 at 3.05.48 PM.png>)

### The generated code

For each edit you make to the Mitosheet, Mito generates code below that corresponds to this edit. As you can see in the screenshot below, we've added a column and set its formula, and the code that we generated does the very same:

![](<../.gitbook/assets/Screen Shot 2022-02-17 at 3.06.35 PM.png>)

#### Running the generated code

Now that you've generated some code, you can run it! By running this generated code, you can lock in the changes you made to your dataframes in the Mitosheet (the edits you make in the mitosheet only apply to a copy of the dataframe by default). To use the edited dataframes in the rest of your analysis, just run the generated code, and keep writing Python below as you normally do!

#### Generated code and replaying an analysis

When you make a `mitosheet.sheet()` call, Mito will automatically generate a analysis ID and write it as the `analysis_to_replay` parameter to this call. This analysis id will also appear in the generated code that Mito writes beneath the cell below - allowing the generated code and the mitosheet call to be linked together.

As long as you pass this `analysis_to_replay` parameter to the `mitosheet.sheet()` call, Mito will attempt to replay that analysis to the mitosheet. Replaying an analysis means applying the same edits that you did in Mito again. See below for an example. 

If you want to start a fresh mitosheet, either make a new `mitosheet.sheet()` call or simply delete the `analysis_to_replay` parameter from an existing mitosheet call. Your generated code will remain below.

##### An example replaying analysis

To illustrate how replaying an analysis works works, consider the example above where we added a column to the Mitosheet, and set it's formula. If we were to then:

1. Rerun the cell importing the `tesla-stock.csv` file as a dataframe.
2. Rerun the cell rendering the mitosheet with `mitosheet.sheet(tesla_stock, analysis_to_replay='id-abcdefg')`

The mitosheet would add the `Movement` column to the dataframe, and set it's formula to `Close - Open` as in the previous analysis. This is because the generated code cell is right below the mitosheet.sheet call, and so Mito attempts to replay this analysis on the new dataframe that is passed (although the dataframe in this case happens to be identical).

Thus, if you switch the dataframe in the `mitosheet.sheet(tesla_stock, analysis_to_replay='id-abcdefg')` call, you need to make sure that the columns you edited in your analysis still exist! If we passed a dataframe of `tesla_stock` to the  `mitosheet.sheet()`call that did not contain the `Open` or `Close` columns, then an error would occur as the formula that the Mitosheet attempts to replay the `analysis_to_replay='id-abcdefg'`, which references those columns, but they no longer exist. Thus, an error would occur.
