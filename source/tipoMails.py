
class tipoMails:
    SISTEMI_PROVVIGIONALIE = "SistemiProvvigionalie"    
    CLIENTE = "Cliente"
    UFFICIO_PROVVIGIONALE="PROV"
    DIREZIONE_CENTRALE_CONSULENTI_FINANZIARI="DCF"
    
    MAIL_GROUPS = {
        SISTEMI_PROVVIGIONALIE: ["brito.grandes@gmail.com","brito.grandes@gmail.com"],        
        CLIENTE: ["brito.grandes@gmail.com"],
        UFFICIO_PROVVIGIONALE:["brito.grandes@gmail.com"],
        DIREZIONE_CENTRALE_CONSULENTI_FINANZIARI:["brito.grandes@gmail.com"]        
    }

    @staticmethod
    def get_emails(group):
        return tipoMails.MAIL_GROUPS.get(group, [])
