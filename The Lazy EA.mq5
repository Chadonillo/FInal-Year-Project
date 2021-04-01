input ENUM_ORDER_TYPE_FILLING fillingType = 1; // Broker Filling Method
input int risk = 1; // % Risk per trade 
input int maxTrades = 3; // Max simultaneous trades.
input int EXPERT_MAGIC = 000419; // Expert's Magic No

datetime now;
string dataFileName = "BackTestData.csv";
string stratFileName = "Strat.txt";
string doneFileName = "Done.txt";
string readyFileName = "Ready.txt";
int LookBackPeriod = 96;
int sell = 0;
int buy = 1;
//---
int filehandleData=INVALID_HANDLE;
int filehandleStrategy=INVALID_HANDLE;
int filehandleDone=INVALID_HANDLE;

double ATR[];
int ATR_handle;

string allSymbols[6] = {"EURUSD","GBPUSD","AUDCAD", "USDCHF", "USDCAD", "USDJPY"};

int OnInit(){
   ATR_handle = iATR(NULL,PERIOD_CURRENT,20);
   FileDelete(dataFileName, FILE_COMMON);
   FileDelete(stratFileName, FILE_COMMON);
   isNewBar();
   writeData();
   notDone();
   return(INIT_SUCCEEDED);
}
  
void OnDeinit(const int reason){
   FileDelete(dataFileName, FILE_COMMON);
   isDone();
}
  
void OnTick(){
   if(isNewBar() && PositionsTotal()<maxTrades){
      if(isPythonReady()){
         ulong currSize = getCurrFileSize();// 
         writeData();
         long direction = waitForDirection(currSize);
         takeTrade(direction);
      }
      else{
         Print("Please run companion app");
      }
      
   }
   //...once per tick code goes here...
}

bool isNewBar(){
   if(now != iTime(NULL,PERIOD_CURRENT,1)){
      now = iTime(NULL,PERIOD_CURRENT,1);
      return true;
   }
   return false;
}

bool isPythonReady(){
   if(FileIsExist(readyFileName, FILE_COMMON)){
      return true;
   }
   return false;
}

void writeData(){
   filehandleData=FileOpen(dataFileName,FILE_WRITE|FILE_SHARE_READ|FILE_CSV|FILE_UNICODE|FILE_COMMON);
   FileWrite(filehandleData, "DateTime", "open", "high", "low", "close");
   int addAmount = LookBackPeriod+63;
   for(int x=addAmount; x>0; x--){
      string time = TimeToString(iTime(NULL,PERIOD_CURRENT,x));
      string open = DoubleToString(iOpen(NULL,PERIOD_CURRENT,x));
      string high = DoubleToString(iHigh(NULL,PERIOD_CURRENT,x));
      string low = DoubleToString(iLow(NULL,PERIOD_CURRENT,x));
      string close = DoubleToString(iClose(NULL,PERIOD_CURRENT,x));
      FileWrite(filehandleData, time, open, high, low, close);
   }
   FileFlush(filehandleData);
   FileClose(filehandleData);
   //Print("sending data");
}

ulong getCurrFileSize(){
   filehandleStrategy=FileOpen(stratFileName,FILE_READ|FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
   ulong size = FileSize(filehandleStrategy);
   return size;
}

long waitForDirection(ulong currFileSize){
   while(FileSize(filehandleStrategy)==currFileSize){
      FileClose(filehandleStrategy);
      filehandleStrategy=FileOpen(stratFileName,FILE_READ|FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_TXT|FILE_ANSI|FILE_COMMON);
   }
   FileSeek(filehandleStrategy, -3, SEEK_END);
   long direction = StringToInteger(FileReadString(filehandleStrategy));
   //Print(direction);
   FileClose(filehandleStrategy);
   return direction;
}

void takeTrade(long typeDir){
   if(typeDir!=2){
      Print(typeDir);
      MqlTradeRequest request={0};
      MqlTradeResult  result = {0};
      request.action   = TRADE_ACTION_DEAL;                     // type of trade operation
      request.symbol   = Symbol();                              // symbol
      //request.volume   = 0.2;                                   // volume of 0.2 lot
      request.magic    = EXPERT_MAGIC;                           // MagicNumber of the order
      request.type_filling = fillingType;
      
      if(typeDir==sell){
         request.type     = ORDER_TYPE_SELL;
         request.price = SymbolInfoDouble(request.symbol,SYMBOL_BID);
      }
      else if(typeDir==buy){
         request.type     = ORDER_TYPE_BUY;
         request.price = SymbolInfoDouble(request.symbol,SYMBOL_ASK);
      }
      request.sl= getATRSl(typeDir,request.price);                           
      request.tp= getATRTp(typeDir,request.price);
      
      request.volume = OptimalLotSize(risk, request.price, request.sl);
      if(!OrderSend(request,result)){
         PrintFormat("OrderSend error %d",GetLastError());
      }
   }
}


void notDone(){
   filehandleDone=FileOpen(doneFileName,FILE_WRITE|FILE_SHARE_READ|FILE_TXT|FILE_ANSI|FILE_COMMON);
   FileWrite(filehandleDone, "0");
   FileFlush(filehandleDone);
   FileClose(filehandleDone);
}

void isDone(){
   filehandleDone=FileOpen(doneFileName,FILE_WRITE|FILE_SHARE_READ|FILE_TXT|FILE_ANSI|FILE_COMMON);
   FileWrite(filehandleDone, "1");
   FileFlush(filehandleDone);
   FileClose(filehandleDone);
}

double getATRSl(long tradeType, double tradePrice){
   CopyBuffer(ATR_handle, 0, 0, 2, ATR);
   ArraySetAsSeries(ATR,true);
   double currATRVal = ATR[1];
   double sl=0;
   if(tradeType == sell){ // Sell
      sl = tradePrice + currATRVal*2;
   }
   
   else if(tradeType == buy){ // Buy
      sl = tradePrice - currATRVal*2;
   }
   return sl;
}

double getATRTp(long tradeType, double tradePrice){
   CopyBuffer(ATR_handle, 0, 0, 2, ATR);
   ArraySetAsSeries(ATR,true);
   double currATRVal = ATR[1];
   double tp=0;
   if(tradeType == sell){ // Sell
      tp = tradePrice - currATRVal*3;
   }
   
   else if(tradeType == buy){ // Buy
      tp = tradePrice + currATRVal*3;
   }
   return tp;
}

double OptimalLotSize(double maxRiskPrc, int maxLossInPips){
  double accBalance = AccountInfoDouble(ACCOUNT_BALANCE);
  double lotSize =  SymbolInfoDouble(_Symbol,SYMBOL_TRADE_CONTRACT_SIZE);
  double tickValue = SymbolInfoDouble(_Symbol,SYMBOL_TRADE_TICK_VALUE);
  if(Digits() <= 3){
   tickValue = tickValue /100;
  }
  double maxLossDollar = accBalance * maxRiskPrc/100;
  double maxLossInQuoteCurr = maxLossDollar / tickValue;
  double a = maxLossInQuoteCurr/(maxLossInPips * _Point)/lotSize;
  double optimalLotSize = NormalizeDouble(maxLossInQuoteCurr /(maxLossInPips * _Point)/lotSize,2);
  return optimalLotSize;
}


double OptimalLotSize(double maxRiskPrc, double entryPrice, double stopLoss){
   int maxLossInPips = MathAbs(entryPrice - stopLoss)/_Point;
   return OptimalLotSize(maxRiskPrc,maxLossInPips);
}
