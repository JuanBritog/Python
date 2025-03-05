DECLARE @Oggi DATE = CAST(GETDATE() AS DATE);
DECLARE @Ieri DATE = DATEADD(DAY, -1, @Oggi);
DECLARE @AltriIeri DATE = DATEADD(DAY, -2, @Oggi);
DECLARE @GiornoDellaSettimana INT = DATEPART(WEEKDAY, @Oggi);

SELECT * FROM (
    -- Dati per oggi (sempre)
    SELECT 
        P.ProcessCode,
        P.ProcessName,
        J.JobStatus,
        S.FieldName as JobStatusDesc,
        CONVERT(VARCHAR, J.StartExecTimestamp, 103) + ' ' + CONVERT(VARCHAR, J.StartExecTimestamp, 108) as StartExecTimestamp
    FROM 
        EMRLCBF1.[dbo].[JAPJobs] AS J WITH (NOLOCK)
    INNER JOIN 
        EMRLCBF1.[dbo].[JAPProcesses] P WITH (NOLOCK) ON J.ProcessCode = P.ProcessCode
    INNER JOIN 
        EMRLCBF1.dbo.Domains S WITH (NOLOCK) ON S.TextValue = J.JobStatus
    WHERE
        S.Field = 'JobStatus' AND
        CAST(J.StartExecTimestamp AS DATE) = @Oggi

    UNION ALL

    -- Dati per ieri (sempre, ma con JobStatus != 'V')
    SELECT 
        P.ProcessCode,
        P.ProcessName,
        J.JobStatus,
        S.FieldName as JobStatusDesc,
        CONVERT(VARCHAR, J.StartExecTimestamp, 103) + ' ' + CONVERT(VARCHAR, J.StartExecTimestamp, 108) as StartExecTimestamp
    FROM 
        EMRLCBF1.dbo.[JAPJobs] AS J WITH (NOLOCK)
    INNER JOIN 
        EMRLCBF1.dbo.[JAPProcesses] P WITH (NOLOCK) ON J.ProcessCode = P.ProcessCode
    INNER JOIN 
        EMRLCBF1.dbo.Domains S WITH (NOLOCK) ON S.TextValue = J.JobStatus
    WHERE
        S.Field = 'JobStatus' AND 
        CAST(J.StartExecTimestamp AS DATE) = @Ieri AND 
        J.JobStatus != 'V'

    UNION ALL

    -- Dati per l'altro ieri (solo se oggi è lunedì)
    SELECT 
        P.ProcessCode,
        P.ProcessName,
        J.JobStatus,
        S.FieldName as JobStatusDesc,
        CONVERT(VARCHAR, J.StartExecTimestamp, 103) + ' ' + CONVERT(VARCHAR, J.StartExecTimestamp, 108) as StartExecTimestamp
    FROM 
        EMRLCBF1.dbo.[JAPJobs] AS J WITH (NOLOCK)
    INNER JOIN 
        EMRLCBF1.dbo.[JAPProcesses] P WITH (NOLOCK) ON J.ProcessCode = P.ProcessCode
    INNER JOIN 
        EMRLCBF1.dbo.Domains S WITH (NOLOCK) ON S.TextValue = J.JobStatus
    WHERE
        S.Field = 'JobStatus' AND 
        CAST(J.StartExecTimestamp AS DATE) = @AltriIeri AND 
        J.JobStatus != 'V' AND
        @GiornoDellaSettimana = 2  -- Questo assicura che questi dati vengano inclusi solo se oggi è lunedì
) AS ResultSet
ORDER BY StartExecTimestamp DESC ,ProcessName ASC;
