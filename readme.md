versione:2
# Python Classes to scraping journal
tramite lo scraping dei siti web prendo infromazioni come:

| journal | url | publication_date | source | img | body_count |
|---------|-----|------------------|--------|-----|------------|

Queste informazioni vengono inserite tutte in un `pandas.DataFrame` e poi salvate su uno spreadsheet

## Note:
- cè un problema con l'eliminazione dei duplicati con la connessione del RDBMS (mysql):

  in sostanza non elimina i duplicati dei dati, e il inserisce duplicati => rivedere la funzione: [`drop_duplicates_from_data_frames`](stupidSpider_1.py#L298-L325)

## Implementazioni
- Finire la classe `StupidSpider_1` con i metodi opportuni.
- Implementare il `threading` per le richieste dei singoli url. Esempio:
    ```python
      def multiprocess_requests(urls:list, max_threads:int | None = None) -> list:
        results:list = []
        if max_threads is None:
            max_threads = int(len(urls) * 0.2 if len(urls) * 0.2 > 20 else len(urls))  # 20% degli articoli
    
        with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
            threads = {executor.submit(my_test,url): url for url in urls}
            for thread in concurrent.futures.as_completed(threads):
                url = threads[thread]
                try:
                    results.append(thread.result())
                except Exception as e:
                    print(f"Error retrieving result for {url}: {e}")
            return results
    ```
- Fare il controllo delle url non sull'intera url ma sull'utlima parte
- Creazione di un log ben stutturato classe `logging` ([vedi `@decorators`](https://www.programmareinpython.it/video-corso-python-intermedio/12-i-decoratori/))
- Implementare con UN API slug per l'invio dei log di errore

## References:
- `Decorators`:
  - https://www.programmareinpython.it/video-corso-python-intermedio/12-i-decoratori/
  - https://www.geeksforgeeks.org/decorators-in-python/
  - https://realpython.com/primer-on-python-decorators/
- `Logging`:
  - https://realpython.com/python-logging/
  - https://www.geeksforgeeks.org/logging-in-python/
  - https://docs.python.org/3/library/logging.html
