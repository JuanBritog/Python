select distinct productFamily, stock.stockcode as codice_titolo, stock.Isin, stock.isinName,sanp.ragsoc CF,  det.customerndg as ndg_cliente, col.ReferenceDate data_report 
from 
EMCMCB01.DBO.CM_Collection  col WITH (NOLOCK), EMCMCB01.DBO.CM_collectionDetail det WITH (NOLOCK) , EMCMCB01.DBO.cm_stockdomain stock WITH (NOLOCK)
, EMCMCB01.DBO.PFFCANA sanp WITH (NOLOCK)
where col.MacroAssetClass='00000' and det.collectionID=col.collectionID and stock.StockCode=col.ProductCode and sanp.ndgcod=financialAdvisorNDG order by productFamily,stock.Isin
