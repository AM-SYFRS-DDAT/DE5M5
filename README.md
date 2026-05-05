# DE5M5
Portfolio development work for Module 5 of Data Engineering Apprenticeship


# Project Plan

## CSV file requirements

### Customers:
- remove NaN from both columns
- Check for duplicates

#### Books:
- remove NaN from Books
- Remove duplicate book titles? -- is this a list of transactions, or a register of books held by the library?
- ensure book titles are capitalised for each word
- change format of Book checkout to datetime, not String

### Questions
- how do you want to aggregate the data in the report? Are there any KPIs?
- how are the files updated and how are they stored?
- how often should the pipeline run? Scheduled or triggered by new checkouts/customer records


### Kanban User Stories
- As a librarian I want to be able to see which books are checked out and which are overdue
- As a manager I want to see the monthly demand for the libarry service - books borrowed, no. of customers, seasonal trends
- As a book buyer I want to see which books are in demand so I can focus my purchases

### Considerations
- which data storage in Azure is most appropriate?