export interface IndexData {
  name: string;
  value: string;
  change: string;
  positive: boolean;
}

export const indices: IndexData[] = [
  { name: "BIST 100", value: "10.642", change: "+%1.28", positive: true },
  { name: "S&P 500", value: "5.482,80", change: "+%0.42", positive: true },
  { name: "NASDAQ", value: "17.143,77", change: "-%0.14", positive: false },
  { name: "DOLAR/TL", value: "36,42", change: "-%0.08", positive: true },
  { name: "EURO/TL", value: "40,24", change: "+%0.23", positive: false },
  { name: "GRAM ALTIN", value: "3.442,80", change: "+%0.96", positive: true },
  { name: "FTSE 100", value: "8.189,95", change: "+%0.35", positive: true },
  { name: "BITCOIN", value: "$68.450", change: "+%2.12", positive: true },
];
