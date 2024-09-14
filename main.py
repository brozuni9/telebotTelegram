import datetime
from binance import Client
import time
import telebot





def variacaoPonderada_BTC():
    try:
        client = Client("","")
        times_kline = [ client.KLINE_INTERVAL_1DAY
                    ,client.KLINE_INTERVAL_12HOUR
                    ,client.KLINE_INTERVAL_6HOUR
                    ,client.KLINE_INTERVAL_4HOUR
                    ,client.KLINE_INTERVAL_1HOUR
                    ,client.KLINE_INTERVAL_30MINUTE
                    ,client.KLINE_INTERVAL_15MINUTE
                    ,client.KLINE_INTERVAL_5MINUTE
                    ,client.KLINE_INTERVAL_1MINUTE
                    ]

        peso = 9
        somaPonderada = 0
        linhaK_low    = 0
        linhaK_high   = 0
        linhaK_close  = 0


        for TIME_INTERVAL in times_kline:
            timeGraf = f"1 day UTC"  if TIME_INTERVAL == '1d'  else f"13 hour ago UTC"  if TIME_INTERVAL == '12h'  else  f"7 hour ago UTC" if TIME_INTERVAL == '6h' else  f"5 hour ago UTC"  if TIME_INTERVAL == '4h'  else  f"2 hour ago UTC"  if TIME_INTERVAL == '1h'  else f"31 minute ago UTC"  if TIME_INTERVAL == '30m'  else  f"16 minute ago UTC"  if TIME_INTERVAL == '15m'  else f"11 minute ago UTC"   if TIME_INTERVAL == '10m' else  f"6 minute ago UTC"   if TIME_INTERVAL == '5m'   else "2 minute ago UTC"        
            klines = client.get_historical_klines('BTCUSDT',TIME_INTERVAL, timeGraf)
            
            linhaK_low   = float(klines[0][3])   
            linhaK_high  = float(klines[0][2])

            VARIACAO = (linhaK_high  - linhaK_low)/ linhaK_low  * 100

            somaPonderada+=VARIACAO/peso
                
            peso=peso-1
    except:
        x=""
    
    p= 0.00001
    p = float(client.get_symbol_ticker(symbol="BTCUSDT")['price'])
    PRECO    = f"{(p-p * 0.001):.0f}"
    PRECO    = float(PRECO) 
    
    utc = f"{datetime.datetime.now(datetime.UTC)}"
    timeGraf = f"{utc[0:10]}" # 2024-07-27                
    #timeGraf = f"27 jan 2024"
    klines = client.get_historical_klines('BTCUSDT','1d', timeGraf) # vela do dia
    
    linhaK_low   = float(klines[0][3])   
    linhaK_high  = float(klines[0][2])
    linhaK_close = float(klines[0][4])
    
    TENDENCIA ="ALTA" if (linhaK_close -  linhaK_low) > (linhaK_high - linhaK_close) else "BAIXA"      
    #print(f"SUBIR {(linhaK_close -  linhaK_low)} > {(linhaK_high - linhaK_close)} CAIR | close {linhaK_close} "          )
    msg_btc =  f"\n######### VARIAÇÃO BTC "
    msg_btc += f"BAIXA" if somaPonderada < 1.5 else "MÉDIA" if somaPonderada < 5.0  else "ALTA"
    msg_btc += f"(${PRECO})\n######## TENDÊNCIA DE {TENDENCIA} \n"


    #print(f"somaPonderada {somaPonderada}")
    return   msg_btc

def buscarInfoCompraVenda(TRADE_SYMBOL, semana):
   
    texto = ""
    client = Client("","")
    TIMES = [client.KLINE_INTERVAL_1WEEK, client.KLINE_INTERVAL_1DAY]

    VARIACAO_BTC = variacaoPonderada_BTC()
    
    PRECO = 0
    p= 0.00001
    p = float(client.get_symbol_ticker(symbol=TRADE_SYMBOL)['price'])
    PRECO    = f"{(p-p * 0.001):.8f}"
    PRECO    = float(PRECO)                                    
    
    texto = f"       🚨  MOEDA {TRADE_SYMBOL} \n|💢 COTAÇÃO ATUAL: ${PRECO:.8f}    "    
    texto+= f"{VARIACAO_BTC}"
    
    for  TIME_INTERVAL in TIMES:
        
        min =1000000
        max = 0

        media_low  = 0.0
        media_high = 0.0

        buscandoLucro = 0        
        lucrandoMomento = 0

        soma_ating_HIGH = 0
        soma_ating_LOW  = 0

        #for semana in semanasBusca:
        QTD_SEMANAS = semana    
        #TIME_INTERVAL = Client.KLINE_INTERVAL_1WEEK
        API_KEY = ""
        API_SECRET= "" 
        closes = []
        
        try:
           
            klines = client.get_historical_klines(TRADE_SYMBOL,TIME_INTERVAL, f"{QTD_SEMANAS} week ago UTC")
            #klines = client.get_historical_klines(TRADE_SYMBOL,TIME_INTERVAL,  "01 Jun, 2024", "21 Jul, 2024")
            
            for candles in klines :
                linhaK_low = float(candles[3])   
                linhaK_high = float(candles[2])   

                media_low  +=linhaK_low
                media_high +=linhaK_high

                if linhaK_low < min:   
                    min = linhaK_low
                if linhaK_high > max:  
                    max = linhaK_high       

                closes.append( [TRADE_SYMBOL,linhaK_low, linhaK_high])


            media_low  = media_low/len(klines)
            media_high = media_high/len(klines)

            buscandoLucro = (media_high-PRECO)/PRECO * 100   ##### buscando lucro acima de 30%
            
            lucrandoMomento = 0
            if PRECO > media_low:
                lucrandoMomento = -(PRECO-media_low)/media_low * 100
            else:
                lucrandoMomento = (media_low-PRECO)/media_low * 100
                    
           
            metrica = f'Semanas' if TIME_INTERVAL=='1w' else 'Dias'    
            soma_ating_HIGH , soma_ating_LOW   = buscaQtdAtingidoMedias(TRADE_SYMBOL,semana, media_low, media_high, TIME_INTERVAL )
            texto+= f"\n"
            texto+= f"- 📉 Mínima período: ${min:.8f}\n-📈 Máxima período: ${max:.8f}\n\n " if TIME_INTERVAL=='1w' else ''
            texto+= f"| Em {metrica}: {len(klines)} \n"
            texto+= f" 🎯 Alvos:\n"
            texto+= f"- 💰COMPRA : ${media_low:.8f}  | {lucrandoMomento:.2f}% de lucro\n"
            texto+= f"- 💰VENDA  : ${media_high:.8f} | {buscandoLucro:.2f}% de lucro\n"
            texto+= f"* ✅ HISTÓRICO EM {len(klines)} {metrica}:\n- OPORT. DE COMPRA EM {soma_ating_HIGH} {metrica} \n- OPORT. DE VENDA EM {soma_ating_LOW} {metrica}\n"
            
        except:
            texto="Não encontramos infomações para essa cripto, verifique a digitação e tente novamente."

           
    return texto

x=""
def buscarMelhorPrecoCompraVenda(TRADE_SYMBOL, semana):
   
    texto = ""
    client = Client("","")
    TIMES = [client.KLINE_INTERVAL_1DAY]

    VARIACAO_BTC = variacaoPonderada_BTC()
    
    PRECO = 0
    p= 0.00001
    p = float(client.get_symbol_ticker(symbol=TRADE_SYMBOL)['price'])
    PRECO    = f"{(p-p * 0.001):.8f}"
    PRECO    = float(PRECO)                                    
    
    texto = f"       🚨  MOEDA {TRADE_SYMBOL} \n|💢 COTAÇÃO ATUAL: ${PRECO:.8f}    "    
    texto+= f"{VARIACAO_BTC}"
    
    for  TIME_INTERVAL in TIMES:
        
        min =1000000
        max = 0

        media_low  = 0.0
        media_high = 0.0

        buscandoLucro = 0        
        lucrandoMomento = 0

        soma_ating_HIGH = 0
        soma_ating_LOW  = 0

        #for semana in semanasBusca:
        QTD_SEMANAS = semana    
        #TIME_INTERVAL = Client.KLINE_INTERVAL_1WEEK
        API_KEY = ""
        API_SECRET= "" 
        closes = []
        
        try:
           
            klines = client.get_historical_klines(TRADE_SYMBOL,TIME_INTERVAL, f"{QTD_SEMANAS} week ago UTC")
            #klines = client.get_historical_klines(TRADE_SYMBOL,TIME_INTERVAL,  "01 Jun, 2024", "21 Jul, 2024")
            
            for candles in klines :
                linhaK_low = float(candles[3])   
                linhaK_high = float(candles[2])   

                media_low  +=linhaK_low
                media_high +=linhaK_high

                if linhaK_low < min:   
                    min = linhaK_low
                if linhaK_high > max:  
                    max = linhaK_high       

                closes.append( [TRADE_SYMBOL,linhaK_low, linhaK_high])


            media_low  = media_low/len(klines)
            media_high = media_high/len(klines)

            buscandoLucro = (media_high-PRECO)/PRECO * 100   ##### buscando lucro acima de 30%
            
            lucrandoMomento = 0
            if PRECO > media_low:
                lucrandoMomento = -(PRECO-media_low)/media_low * 100
            else:
                lucrandoMomento = (media_low-PRECO)/media_low * 100
                    
           
            metrica = f'Semanas' if TIME_INTERVAL=='1w' else 'Dias'    
            soma_ating_HIGH , soma_ating_LOW   = buscaQtdAtingidoMedias(TRADE_SYMBOL,semana, media_low, media_high, TIME_INTERVAL )
            texto+= f"\n"
            texto+= f"- 📉 Mínima período: ${min:.8f}\n-📈 Máxima período: ${max:.8f}\n\n " if TIME_INTERVAL=='1w' else ''
            texto+= f"| Em {metrica}: {len(klines)} \n"
            texto+= f" 🎯 Alvos:\n"
            texto+= f"- 💰COMPRA : ${media_low:.8f}  | {lucrandoMomento:.2f}% de lucro\n"
            texto+= f"- 💰VENDA  : ${media_high:.8f} | {buscandoLucro:.2f}% de lucro\n"
            texto+= f"* ✅ HISTÓRICO EM {len(klines)} {metrica}:\n- OPORT. DE COMPRA EM {soma_ating_HIGH} {metrica} \n- OPORT. DE VENDA EM {soma_ating_LOW} {metrica}\n"
            
        except:
            texto="Não encontramos infomações para essa cripto, verifique a digitação e tente novamente."

        
    if texto != "":
        print("#############################################################################################################")

    return texto, media_low, media_high, PRECO, min, max, lucrandoMomento, buscandoLucro,soma_ating_HIGH,soma_ating_LOW

#############################################################################################################
#############################################################################################################
#############################################################################################################

########################    IMPORTA QTD_VEZES ATINGIU AS MÉDIAS NO PERIODO ###################################
########################    IMPORTA QTD_VEZES ATINGIU AS MÉDIAS NO PERIODO ###################################
########################    IMPORTA QTD_VEZES ATINGIU AS MÉDIAS NO PERIODO ###################################
########################    IMPORTA QTD_VEZES ATINGIU AS MÉDIAS NO PERIODO ###################################

#############################################################################################################
#############################################################################################################
#############################################################################################################


def buscaQtdAtingidoMedias(TRADE_SYMBOL,diasBusca, MEDIA_LOW, MEDIA_HIGH,  TIME_INTER = '1d'):
    QTD_DIAS = diasBusca    
    #TIME_INTERVAL = Client.KLINE_INTERVAL_1MINUTE
    TIME_INTERVAL = '1d' if TIME_INTER=='1d' else TIME_INTER 


    client = Client("","")
    tempo       = f"day" if TIME_INTERVAL=='1d' else "week" 
    QTD_DIAS    = QTD_DIAS*7 if TIME_INTERVAL=='1d' else QTD_DIAS     
    klines = client.get_historical_klines(TRADE_SYMBOL,TIME_INTERVAL, f"{QTD_DIAS} {tempo} ago UTC")
      
    soma_ating_HIGH  = 0
    soma_ating_LOW   = 0

    for candles in klines :
        linhaK_HIGH = float(candles[2])   
        linhaK_LOW = float(candles[3])   
                     
        ########### IDEIA É VALIDAR SE ELE BATE O PRECO MEDIO HIGH NAQUELA HORA E NAS DEMAIS HORA NÃO BATEU, ATÉ VOLTAR A BATER NOVAMENTE
        if(linhaK_HIGH >= MEDIA_HIGH ):
            soma_ating_HIGH+=1

        ########### IDEIA É VALIDAR SE ELE BATE O PRECO MEDIO LOW NAQUELA HORA E NAS DEMAIS HORA NÃO BATEU, ATÉ VOLTAR A BATER NOVAMENTE
        if(linhaK_LOW <= MEDIA_LOW ):
            soma_ating_LOW+=1


    return  soma_ating_HIGH , soma_ating_LOW     


#############################################################################################################
#############################################################################################################
#############################################################################################################

########################                sistema telebot                      ###############################
########################                sistema telebot                      ###############################
########################                sistema telebot                      ###############################
########################                sistema telebot                      ###############################
                    
#############################################################################################################
#############################################################################################################
#############################################################################################################


CHAVE_API = "7217727659:AAE9X63Tx3K9vVcvP3DIfDEC7COo_bzKAW0"

bot = telebot.TeleBot(CHAVE_API)		

ID_ADM = 824001475
def enviarMsgADM(msg):
    bot.send_message(ID_ADM, msg) 
    
            
def verificar(mensagem):
    RETORNO  = True
    try:
        if ID_ADM == mensagem.chat.id:
            enviarMsgADM(f'Outros utilizadores: {mensagem.chat.text}')
    except:
        pass
     
    return RETORNO    


@bot.message_handler(func=verificar)
def responder(mensagem):
    try:
        msg = mensagem.text.replace("/","").replace(" ","").upper()
        texto=""

        if(mensagem.text.upper() == "/START"):
            texto = """
            Escolha uma cripto para continuar ou digite o nome como exemplo BTCUSDT
            
            /GALAUSDT
            /ADAUSDT
            /ILVUSDT
            /PEPEUSDT
            /ONEUSDT
            /ASTUSDT
            /ETHUSD\n
            
            """
            bot.reply_to(mensagem, texto)
            return
        else:
            bot.reply_to(mensagem, f"Aguade, já te trago informações sobre {msg}")

        if(mensagem.text.find('AÇÃO:')!=0):    
            tempo = 9
            if (len(msg.split(",")) > 1):
                tempo = msg.split(",")[1]
                msg   = msg.split(",")[0]
                
            msg = msg if(msg.find("USDT") > 0 or msg.find("BRL") > 0) else msg+'USDT'
            
            print (f"{msg} - {tempo}")
            texto = buscarInfoCompraVenda(msg, int(tempo))
            bot.send_message(mensagem.chat.id, texto)
    except:
        try:    
            bot.send_message(mensagem.chat.id, "NÃO É POSSIVEL RESPONDER A ESSE CONTEÚDO!")
        except:
            pass

bot.polling()

#print(buscarInfoCompraVenda("BTCUSDT", 9))