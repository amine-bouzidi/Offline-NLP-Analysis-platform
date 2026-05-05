"""
corpus_kpmg.py
Corpus de 100 textes réalistes pour le Due Diligence Réputationnel KPMG
Langues : FR, EN, AR, DE, ES
Catégories : audit_conformite, reputation_scandale, services_qualite, rh_management,
             finance_performance, partenariat_strategie, innovation_tech, rse_ethique
Sources : presse, réseaux sociaux, avis vérifiés, forums
"""

CORPUS_KPMG = [

    # ─────────────────────────────────────────────────────────
    # CATÉGORIE 1 : AUDIT ET CONFORMITÉ (15 textes)
    # ─────────────────────────────────────────────────────────
    {
        'id': 1, 'language': 'fr', 'category': 'audit_conformite',
        'source_type': 'press',
        'text': "Le cabinet Deloitte a été épinglé par l'AMF pour des manquements graves dans ses procédures d'audit sur trois sociétés cotées. Les commissaires aux comptes n'auraient pas détecté des irrégularités comptables pourtant visibles dans les états financiers. Une amende de 2 millions d'euros a été prononcée."
    },
    {
        'id': 2, 'language': 'en', 'category': 'audit_conformite',
        'source_type': 'press',
        'text': "PwC Australia faces a major scandal after it was revealed that partners shared confidential government tax policy information with clients to help them avoid new tax measures. The scandal has prompted calls for stricter regulation of the Big Four accounting firms and led to the resignation of several senior partners."
    },
    {
        'id': 3, 'language': 'ar', 'category': 'audit_conformite',
        'source_type': 'press',
        'text': "كشف تقرير هيئة الرقابة المالية عن إخفاقات جسيمة في عمليات التدقيق التي أجرتها إحدى شركات المحاسبة الكبرى على مجموعة من الشركات المدرجة في السوق المالية. وأشار التقرير إلى أن المدققين أغفلوا مخالفات محاسبية صريحة وتجاهلوا إشارات التحذير المبكرة من الاحتيال المالي."
    },
    {
        'id': 4, 'language': 'de', 'category': 'audit_conformite',
        'source_type': 'press',
        'text': "Der Wirecard-Skandal hat das Vertrauen in die deutsche Wirtschaftsprüfungsbranche erschüttert. EY wurde vorgeworfen, jahrelang Bilanzfälschungen in Milliardenhöhe nicht aufgedeckt zu haben. Der Bundestagsuntersuchungsausschuss fordert nun strengere Regulierung und häufigere Rotation der Prüfer."
    },
    {
        'id': 5, 'language': 'es', 'category': 'audit_conformite',
        'source_type': 'press',
        'text': "La CNMV ha sancionado a una de las grandes firmas de auditoría por no detectar irregularidades contables en los estados financieros de una empresa del IBEX 35. Los auditores habrían omitido señales claras de manipulación de beneficios durante tres ejercicios consecutivos, lo que causó pérdidas millonarias a los inversores."
    },
    {
        'id': 6, 'language': 'fr', 'category': 'audit_conformite',
        'source_type': 'social',
        'text': "Encore un cabinet d'audit qui se fait attraper la main dans le sac. La régulation de ces Big Four est une vraie blague, ils auditent les mêmes boîtes depuis 20 ans et personne ne voit rien. Conflit d'intérêts évident. Il faut une rotation obligatoire tous les 5 ans minimum."
    },
    {
        'id': 7, 'language': 'en', 'category': 'audit_conformite',
        'source_type': 'verified',
        'text': "As a CFO who has worked with multiple Big Four firms, I can say that audit quality varies enormously depending on the team assigned. We switched auditors after our previous firm missed a significant revenue recognition issue. The new team caught it immediately during their first review."
    },
    {
        'id': 8, 'language': 'ar', 'category': 'audit_conformite',
        'source_type': 'social',
        'text': "هل تساءلتم يوماً لماذا تفشل شركات التدقيق الكبرى في اكتشاف الاحتيال المالي رغم تقاضيها ملايين الدولارات؟ السبب بسيط: المراجع المالي يعمل لصالح من يدفع له. النموذج الحالي للتدقيق مكسور بطبيعته ويحتاج إلى إصلاح جذري."
    },
    {
        'id': 9, 'language': 'de', 'category': 'audit_conformite',
        'source_type': 'verified',
        'text': "Unsere Erfahrung mit dem Audit-Team war insgesamt positiv. Die Prüfer waren gründlich und haben auch kritische Fragen gestellt. Allerdings haben wir festgestellt, dass die Qualität stark vom jeweiligen Prüfungsleiter abhängt. Beim Wechsel des Teams haben wir deutliche Unterschiede gemerkt."
    },
    {
        'id': 10, 'language': 'es', 'category': 'audit_conformite',
        'source_type': 'social',
        'text': "El escándalo de auditoría de esta semana demuestra lo que muchos sabíamos: las grandes firmas priorizan mantener al cliente feliz sobre hacer su trabajo correctamente. Cuando tu cliente paga 10 millones en honorarios, ¿realmente vas a señalar sus irregularidades? El sistema está roto."
    },
    {
        'id': 11, 'language': 'fr', 'category': 'audit_conformite',
        'source_type': 'press',
        'text': "Le Haut Conseil du Commissariat aux Comptes publie son rapport annuel sur la qualité des audits en France. Les résultats montrent une amélioration globale mais pointent des lacunes persistantes dans l'audit des instruments financiers complexes et des transactions avec les parties liées."
    },
    {
        'id': 12, 'language': 'en', 'category': 'audit_conformite',
        'source_type': 'press',
        'text': "KPMG has agreed to pay $200 million to settle SEC charges related to audit failures at several client companies. The regulator found that KPMG partners had improperly obtained confidential information about upcoming inspections. The settlement includes enhanced compliance measures and independent monitoring."
    },
    {
        'id': 13, 'language': 'ar', 'category': 'audit_conformite',
        'source_type': 'verified',
        'text': "تعاملنا مع فريق التدقيق على مدار ثلاث سنوات وكانت التجربة مهنية بامتياز. الفريق كان دقيقاً في عمله ومحترفاً في تعاملاته، وأبدى ملاحظات بناءة ساعدتنا على تحسين إجراءاتنا المحاسبية الداخلية. نوصي بهم لأي شركة تبحث عن مدقق موثوق."
    },
    {
        'id': 14, 'language': 'de', 'category': 'audit_conformite',
        'source_type': 'press',
        'text': "Die Wirtschaftsprüferkammer verschärft die Qualitätskontrolle für Prüfungsgesellschaften nach mehreren Skandalen. Ab 2025 müssen alle börsennotierten Unternehmen ihre Abschlussprüfer alle zehn Jahre wechseln. Experten begrüßen die Maßnahme, warnen aber vor steigenden Prüfungskosten."
    },
    {
        'id': 15, 'language': 'es', 'category': 'audit_conformite',
        'source_type': 'verified',
        'text': "Llevamos cinco años trabajando con el mismo equipo de auditoría y el servicio ha sido excelente. Son rigurosos, siempre disponibles para consultas y sus informes son claros y detallados. Han añadido valor real a nuestra empresa más allá de la simple verificación contable."
    },

    # ─────────────────────────────────────────────────────────
    # CATÉGORIE 2 : RÉPUTATION ET SCANDALES (15 textes)
    # ─────────────────────────────────────────────────────────
    {
        'id': 16, 'language': 'fr', 'category': 'reputation_scandale',
        'source_type': 'press',
        'text': "Le cabinet McKinsey est au cœur d'une polémique après la publication d'un livre révélant ses liens avec des régimes autoritaires et son rôle dans la crise des opioïdes aux États-Unis. Plusieurs grandes entreprises ont annoncé suspendre leurs contrats avec le cabinet en attendant les conclusions d'une enquête indépendante."
    },
    {
        'id': 17, 'language': 'en', 'category': 'reputation_scandale',
        'source_type': 'press',
        'text': "Boston Consulting Group faces reputational damage after leaked internal documents revealed that consultants advised a major pharmaceutical company on strategies to maximize opioid sales while downplaying addiction risks. The revelations have led to calls for greater transparency in the consulting industry."
    },
    {
        'id': 18, 'language': 'ar', 'category': 'reputation_scandale',
        'source_type': 'social',
        'text': "فضيحة جديدة تهز عالم الاستشارات المالية. وثائق مسربة تكشف أن شركة استشارات كبرى نصحت عملاءها بتحويل أرباحهم إلى ملاذات ضريبية مع علمها التام بأن هذه الممارسات تضر بالمصلحة العامة. هل آن الأوان لمحاسبة هذه الشركات على أضرارها الاجتماعية؟"
    },
    {
        'id': 19, 'language': 'de', 'category': 'reputation_scandale',
        'source_type': 'press',
        'text': "Ein führendes Beratungsunternehmen steht unter Verdacht, vertrauliche Regierungsinformationen an private Kunden weitergegeben zu haben. Die Staatsanwaltschaft hat Ermittlungen eingeleitet. Das Unternehmen bestreitet alle Vorwürfe und betont sein Engagement für ethisches Geschäftsgebaren."
    },
    {
        'id': 20, 'language': 'es', 'category': 'reputation_scandale',
        'source_type': 'press',
        'text': "Una reconocida firma de consultoría estratégica se ve envuelta en un escándalo de puertas giratorias al conocerse que varios de sus socios principales pasaron directamente de altos cargos gubernamentales a asesorar a empresas que regulaban. El caso ha reabierto el debate sobre los conflictos de interés en el sector."
    },
    {
        'id': 21, 'language': 'fr', 'category': 'reputation_scandale',
        'source_type': 'social',
        'text': "Ces cabinets de conseil qui conseillent l'État et les entreprises privées en même temps, c'est un conflit d'intérêts permanent. Comment peut-on faire confiance à leurs recommandations quand ils jouent sur les deux tableaux ? La réglementation doit absolument évoluer sur ce point."
    },
    {
        'id': 22, 'language': 'en', 'category': 'reputation_scandale',
        'source_type': 'social',
        'text': "Just read the exposé on that consulting firm's involvement in the opioid crisis. These companies optimize for profit with zero regard for human consequences. They hide behind client confidentiality while their advice destroys communities. Time for real accountability in the consulting industry."
    },
    {
        'id': 23, 'language': 'ar', 'category': 'reputation_scandale',
        'source_type': 'press',
        'text': "تحقيق استقصائي يكشف أن شركة استشارات دولية كبرى قدمت توصيات متناقضة لعملاء متنافسين في نفس القطاع، مما يثير تساؤلات جدية حول مدى التزامها بمبادئ السرية المهنية وتجنب تضارب المصالح. الشركة نفت الاتهامات وأكدت وجود جدران عازلة صارمة بين فرقها."
    },
    {
        'id': 24, 'language': 'de', 'category': 'reputation_scandale',
        'source_type': 'social',
        'text': "Ich frage mich, warum niemand diese Beratungsunternehmen zur Rechenschaft zieht, wenn ihre Empfehlungen zu Massenentlassungen oder Unternehmenszusammenbrüchen führen. Sie kassieren ihre Millionenhonorare und sind dann weg. Keine Haftung, keine Konsequenzen. Das System ist grundlegend falsch."
    },
    {
        'id': 25, 'language': 'es', 'category': 'reputation_scandale',
        'source_type': 'social',
        'text': "La reputación de estas grandes consultoras está por los suelos después de tantos escándalos. Primero el caso de los opioídes, luego las puertas giratorias, ahora el tema del asesoramiento fiscal agresivo. ¿Cuándo van a exigirles responsabilidades reales por el daño que causan?"
    },
    {
        'id': 26, 'language': 'fr', 'category': 'reputation_scandale',
        'source_type': 'press',
        'text': "Accenture fait face à un recours collectif de ses anciens employés qui dénoncent une culture de travail toxique et des pratiques discriminatoires. Les plaignants allèguent que le cabinet favorise systématiquement certains profils au détriment de la diversité malgré ses engagements publics affichés."
    },
    {
        'id': 27, 'language': 'en', 'category': 'reputation_scandale',
        'source_type': 'verified',
        'text': "We terminated our contract with the firm after discovering they had shared our proprietary market data with a competitor client. Despite their assurances about information barriers, it was clear those barriers didn't exist in practice. The reputational damage to our company was significant and we are pursuing legal action."
    },
    {
        'id': 28, 'language': 'ar', 'category': 'reputation_scandale',
        'source_type': 'verified',
        'text': "أنهينا تعاملنا مع الشركة الاستشارية إثر اكتشافنا أن مستشاريهم كانوا يقدمون لنا توصيات متحيزة لصالح موردين معينين لهم علاقات تجارية معهم. الأمانة والاستقلالية شرطان أساسيان في أي علاقة استشارية، وللأسف لم نجدهما هناك."
    },
    {
        'id': 29, 'language': 'de', 'category': 'reputation_scandale',
        'source_type': 'press',
        'text': "Neue Recherchen zeigen, dass eine internationale Unternehmensberatung ihre Regierungsmandate genutzt haben soll, um Wettbewerbsvorteile für ihre Privatkunden zu sichern. Der Skandal wirft grundlegende Fragen über Interessenkonflikte im Beratungssektor auf und fordert eine schärfere Regulierung."
    },
    {
        'id': 30, 'language': 'es', 'category': 'reputation_scandale',
        'source_type': 'verified',
        'text': "Tuvimos una experiencia muy negativa con esta firma. Sus consultores presentaron un informe estratégico que luego descubrimos era casi idéntico al que habían presentado a un competidor nuestro. La falta de originalidad y el evidente conflicto de intereses nos llevó a romper el contrato inmediatamente."
    },

    # ─────────────────────────────────────────────────────────
    # CATÉGORIE 3 : SERVICES ET QUALITÉ (15 textes)
    # ─────────────────────────────────────────────────────────
    {
        'id': 31, 'language': 'fr', 'category': 'services_qualite',
        'source_type': 'verified',
        'text': "Notre collaboration avec ce cabinet de conseil a été très satisfaisante. Les consultants ont fait preuve d'une grande expertise dans notre secteur et ont livré des analyses pertinentes qui ont directement influencé notre stratégie d'expansion. Le rapport qualité-prix est excellent pour une firme de ce calibre."
    },
    {
        'id': 32, 'language': 'en', 'category': 'services_qualite',
        'source_type': 'verified',
        'text': "The consulting team exceeded our expectations on every front. Their due diligence report was thorough, well-structured and identified risks we hadn't considered. The team was responsive, professional and demonstrated deep industry knowledge. We will definitely work with them again on future projects."
    },
    {
        'id': 33, 'language': 'ar', 'category': 'services_qualite',
        'source_type': 'verified',
        'text': "قدمت لنا الشركة الاستشارية خدمة احترافية رفيعة المستوى. فريق العمل كان على دراية واسعة بقطاعنا، وقدم تحليلات دقيقة ساعدتنا على اتخاذ قرارات استثمارية مدروسة. التقرير النهائي كان شاملاً ومفصلاً وتجاوز توقعاتنا من حيث الجودة والعمق."
    },
    {
        'id': 34, 'language': 'de', 'category': 'services_qualite',
        'source_type': 'verified',
        'text': "Die Beratungsleistung war insgesamt hervorragend. Das Team hat unsere Branche schnell durchdrungen und lieferte innerhalb kurzer Zeit wertvolle Einblicke. Besonders beeindruckend war die Qualität der Datenanalyse und die Klarheit der strategischen Empfehlungen. Wir würden sie uneingeschränkt weiterempfehlen."
    },
    {
        'id': 35, 'language': 'es', 'category': 'services_qualite',
        'source_type': 'verified',
        'text': "El equipo de consultoría demostró un conocimiento profundo de nuestro sector y entregó un análisis estratégico de alta calidad. Las recomendaciones fueron prácticas, bien fundamentadas y adaptadas a nuestra realidad empresarial. La comunicación fue fluida durante todo el proyecto y los plazos se cumplieron."
    },
    {
        'id': 36, 'language': 'fr', 'category': 'services_qualite',
        'source_type': 'social',
        'text': "J'ai travaillé avec plusieurs cabinets de conseil au cours de ma carrière et honnêtement les écarts de qualité sont énormes. Certains livrent des rapports génériques copiés-collés d'un client à l'autre. Les meilleurs s'imprègnent vraiment de votre réalité et ça fait toute la différence."
    },
    {
        'id': 37, 'language': 'en', 'category': 'services_qualite',
        'source_type': 'social',
        'text': "Consulting quality is really hit or miss. Had an amazing experience with one firm that completely transformed our operations and a terrible one with another that delivered a generic slide deck with our logo on it. The difference often comes down to the specific partner leading your engagement."
    },
    {
        'id': 38, 'language': 'ar', 'category': 'services_qualite',
        'source_type': 'social',
        'text': "تجارب متباينة مع شركات الاستشارات الكبرى. بعضها يقدم خدمة احترافية حقيقية تضيف قيمة ملموسة لعملك، والبعض الآخر يبيع لك تقارير جاهزة بأسمائك عليها. الفارق الحقيقي يكمن في مدى فهم الفريق لخصوصية قطاعك وتحدياتك."
    },
    {
        'id': 39, 'language': 'de', 'category': 'services_qualite',
        'source_type': 'verified',
        'text': "Wir haben mit dem Beratungsunternehmen ein komplexes Restrukturierungsprojekt durchgeführt. Die Qualität der Arbeit war hoch, aber die Kosten waren erheblich. Letztendlich hat sich die Investition gelohnt, da die empfohlenen Maßnahmen zu einer deutlichen Effizienzsteigerung geführt haben."
    },
    {
        'id': 40, 'language': 'es', 'category': 'services_qualite',
        'source_type': 'social',
        'text': "La calidad del servicio de consultoría depende enormemente del equipo asignado. Con el mismo proveedor tuvimos una experiencia excelente en el primer proyecto y mediocre en el segundo porque cambiaron al equipo. La continuidad del equipo es crucial para mantener la calidad del servicio."
    },
    {
        'id': 41, 'language': 'fr', 'category': 'services_qualite',
        'source_type': 'press',
        'text': "Une étude comparative des cabinets de conseil publiée par le Financial Times classe les Big Four en termes de satisfaction client. KPMG se distingue par sa proximité avec les PME et ETI tandis que McKinsey et BCG dominent sur les grands comptes. La spécialisation sectorielle ressort comme le facteur clé de satisfaction."
    },
    {
        'id': 42, 'language': 'en', 'category': 'services_qualite',
        'source_type': 'press',
        'text': "Client satisfaction surveys in the consulting industry show growing dissatisfaction with value for money. While technical expertise remains high, clients increasingly question whether the astronomical fees charged by top firms are justified given the mixed track record of implementation success."
    },
    {
        'id': 43, 'language': 'ar', 'category': 'services_qualite',
        'source_type': 'press',
        'text': "استطلاع رأي عملاء شركات الاستشارات في المنطقة العربية يكشف عن مستوى رضا متوسط. يُثني العملاء على الكفاءة التقنية لهذه الشركات لكنهم يشككون في مدى تكييف حلولها مع الخصوصية الثقافية والتنظيمية للأسواق العربية. الطلب على الاستشارات المحلية المتخصصة يتنامى."
    },
    {
        'id': 44, 'language': 'de', 'category': 'services_qualite',
        'source_type': 'social',
        'text': "Als jemand, der auf beiden Seiten des Tisches saß – als Berater und als Klient – kann ich sagen: Der größte Mehrwert entsteht, wenn das Beratungsteam wirklich zuhört und die Empfehlungen auf die spezifische Situation des Unternehmens zuschneidet. Generische Ansätze sind Geldverschwendung."
    },
    {
        'id': 45, 'language': 'es', 'category': 'services_qualite',
        'source_type': 'press',
        'text': "El mercado de consultoría en España registra un crecimiento del 12% impulsado por la demanda de servicios de transformación digital y sostenibilidad. Sin embargo, la escasez de talento especializado amenaza la capacidad de las firmas para mantener sus estándares de calidad ante el aumento de la demanda."
    },

    # ─────────────────────────────────────────────────────────
    # CATÉGORIE 4 : RH ET MANAGEMENT (12 textes)
    # ─────────────────────────────────────────────────────────
    {
        'id': 46, 'language': 'fr', 'category': 'rh_management',
        'source_type': 'social',
        'text': "Ex-consultant Big Four ici. La réalité derrière le prestige : 80 heures par semaine, management par la peur, turnover de 30% par an et une culture qui broie les gens. Les clients paient pour des seniors et reçoivent des juniors de 23 ans qui n'ont aucune expérience réelle du business."
    },
    {
        'id': 47, 'language': 'en', 'category': 'rh_management',
        'source_type': 'social',
        'text': "Worked at a Big Four for 4 years. The culture is brutal: constant pressure to bill hours, fear-based management, and a pyramid structure designed so most people leave before making partner. The work can be interesting but the human cost is enormous. Burnout is the norm, not the exception."
    },
    {
        'id': 48, 'language': 'ar', 'category': 'rh_management',
        'source_type': 'social',
        'text': "استقلت من شركة الاستشارات بعد عامين من الضغط المتواصل وساعات العمل الجنونية. الوعود التي قطعوها عند التوظيف لم تتحقق، والتوازن بين العمل والحياة الشخصية كان شبه معدوم. لا أنصح بهذا المسار المهني إلا لمن هو مستعد لتضحيات جسيمة."
    },
    {
        'id': 49, 'language': 'de', 'category': 'rh_management',
        'source_type': 'social',
        'text': "Nach drei Jahren bei einer der großen Unternehmensberatungen habe ich gekündigt. Die Arbeitsbelastung war nicht nachhaltig, die Unternehmenskultur toxisch und die versprochene Work-Life-Balance existierte nur auf dem Papier. Die Beförderungsversprechen waren vage und das echte Lernen blieb aus."
    },
    {
        'id': 50, 'language': 'es', 'category': 'rh_management',
        'source_type': 'social',
        'text': "Tras cinco años en consultoría estratégica, puedo decir que la experiencia te forma profesionalmente pero te destruye personalmente. La cultura del presentismo, la presión constante y la competencia interna hacen que la rotación sea altísima. Las firmas saben esto y lo aceptan como parte del modelo de negocio."
    },
    {
        'id': 51, 'language': 'fr', 'category': 'rh_management',
        'source_type': 'press',
        'text': "Une étude de Glassdoor révèle que les cabinets de conseil figurent parmi les employeurs avec les scores de bien-être les plus bas malgré des salaires élevés. Le taux de rotation annuel dépasse 25% dans les Big Four, ce qui soulève des questions sur la soutenabilité de leur modèle opérationnel."
    },
    {
        'id': 52, 'language': 'en', 'category': 'rh_management',
        'source_type': 'press',
        'text': "Consulting firms are facing a talent crisis as Gen Z workers increasingly reject the grueling hours and up-or-out culture that defined the industry. Firms are being forced to rethink their employee value proposition, offering more flexibility, mental health support and clearer career progression."
    },
    {
        'id': 53, 'language': 'ar', 'category': 'rh_management',
        'source_type': 'press',
        'text': "تواجه شركات الاستشارات الكبرى أزمة استقطاب مواهب حادة في ظل تنافس متصاعد من شركات التكنولوجيا التي تقدم ظروف عمل أفضل وثقافة أكثر صحة. الجيل الجديد من الخريجين يرفض نموذج العمل الاستشاري التقليدي ويبحث عن معنى أعمق في مسيرته المهنية."
    },
    {
        'id': 54, 'language': 'de', 'category': 'rh_management',
        'source_type': 'press',
        'text': "Unternehmensberatungen kämpfen um Talente: Immer mehr High Potentials bevorzugen Technologieunternehmen oder Startups gegenüber klassischen Beratungskarrieren. Die Branche reagiert mit flexibleren Arbeitsmodellen, höheren Gehältern und neuen Karrierepfaden außerhalb der traditionellen Partner-Pyramide."
    },
    {
        'id': 55, 'language': 'es', 'category': 'rh_management',
        'source_type': 'verified',
        'text': "Como ex-empleado de una firma de consultoría, debo reconocer que la formación y el aprendizaje que recibí fueron excepcionales. Sin embargo, la cultura de trabajo no era sostenible a largo plazo. La firma ha mejorado mucho en los últimos años con iniciativas de bienestar, pero aún queda camino por recorrer."
    },
    {
        'id': 56, 'language': 'fr', 'category': 'rh_management',
        'source_type': 'verified',
        'text': "J'ai passé 6 ans dans un cabinet de conseil et je garde un bilan mitigé. La formation était excellente, l'exposition à des problématiques variées incomparable. Mais le coût humain est réel. J'ai vu des collègues brillants se brûler les ailes. Il faut y aller les yeux ouverts."
    },
    {
        'id': 57, 'language': 'en', 'category': 'rh_management',
        'source_type': 'verified',
        'text': "My experience at the firm was overall positive. The training programs are world-class and the exposure to senior leadership and complex business problems accelerated my development enormously. The hours were long but manageable with good time management. I left on good terms to pursue an industry role."
    },

    # ─────────────────────────────────────────────────────────
    # CATÉGORIE 5 : FINANCE ET PERFORMANCE (12 textes)
    # ─────────────────────────────────────────────────────────
    {
        'id': 58, 'language': 'fr', 'category': 'finance_performance',
        'source_type': 'press',
        'text': "Les résultats financiers du groupe Capgemini pour le premier semestre dépassent les attentes des analystes avec une croissance du chiffre d'affaires de 8,3% en organique. La marge opérationnelle s'améliore de 40 points de base à 13,2% grâce aux efforts de productivité et à la montée en gamme des offres."
    },
    {
        'id': 59, 'language': 'en', 'category': 'finance_performance',
        'source_type': 'press',
        'text': "Accenture reports strong quarterly earnings with revenue growth of 9% in constant currency, driven by continued demand for digital transformation and AI services. The company raises its full-year guidance and announces a $3 billion share buyback program, signaling confidence in its financial outlook."
    },
    {
        'id': 60, 'language': 'ar', 'category': 'finance_performance',
        'source_type': 'press',
        'text': "أعلنت شركة ماكنزي عن نتائج مالية قياسية للعام الماضي مع نمو في الإيرادات تجاوز 15%. هذا الأداء يعكس الطلب المتزايد على خدمات التحول الرقمي والاستشارات المتعلقة بالذكاء الاصطناعي. الشركة تخطط للتوسع في الأسواق الناشئة وخاصة منطقة الشرق الأوسط وأفريقيا."
    },
    {
        'id': 61, 'language': 'de', 'category': 'finance_performance',
        'source_type': 'press',
        'text': "Die Deutsche Unternehmensberatung Roland Berger verzeichnet trotz schwieriger Konjunktur ein Umsatzwachstum von 7%. Besonders die Bereiche Restrukturierung und digitale Transformation boomen. Die Firma plant, 500 neue Berater einzustellen und ihre Präsenz in Asien auszubauen."
    },
    {
        'id': 62, 'language': 'es', 'category': 'finance_performance',
        'source_type': 'press',
        'text': "El sector de consultoría en España cierra el año con un crecimiento del 15% en facturación, impulsado principalmente por proyectos de transformación digital y asesoramiento en ESG. Las grandes firmas internacionales consolidan su liderazgo mientras emergen boutiques especializadas con propuestas de valor diferenciadas."
    },
    {
        'id': 63, 'language': 'fr', 'category': 'finance_performance',
        'source_type': 'social',
        'text': "Les marges des cabinets de conseil sont obscènes. Ils facturent 3000€ la journée consultant et paient leurs juniors 45k€ par an. Le modèle économique repose entièrement sur l'exploitation de jeunes diplômés ambitieux. C'est un système qui mérite d'être questionnné sérieusement."
    },
    {
        'id': 64, 'language': 'en', 'category': 'finance_performance',
        'source_type': 'social',
        'text': "The consulting business model is essentially arbitrage: hire smart young people cheap, charge clients 10x their cost, and pocket the difference. McKinsey makes 40% margins. Their clients often don't. Maybe that tells you something about whose interests they're actually serving."
    },
    {
        'id': 65, 'language': 'ar', 'category': 'finance_performance',
        'source_type': 'social',
        'text': "هوامش الربح الفلكية لشركات الاستشارات الكبرى تطرح تساؤلات مشروعة. تدفع للمستشار المبتدئ راتباً متواضعاً وتفاتر العميل بمبالغ مضاعفة عشرات المرات. من يستفيد حقاً من هذه المعادلة؟ الشركات أم العملاء الذين يمولونها بسخاء؟"
    },
    {
        'id': 66, 'language': 'de', 'category': 'finance_performance',
        'source_type': 'press',
        'text': "Eine Analyse der Honorarstrukturen im Beratungssektor zeigt, dass Tagessätze für erfahrene Berater in Deutschland zwischen 2.000 und 5.000 Euro liegen. Kritiker fragen, ob diese Kosten immer durch den tatsächlichen Mehrwert gerechtfertigt werden. Transparenz bei der Honorarabrechnung wird zunehmend gefordert."
    },
    {
        'id': 67, 'language': 'es', 'category': 'finance_performance',
        'source_type': 'social',
        'text': "Los honorarios de las grandes consultoras son astronómicos y no siempre justificados por los resultados. He visto proyectos de transformación que costaron decenas de millones y terminaron en fracaso. La industria necesita más accountability y métricas claras de retorno sobre la inversión en consultoría."
    },
    {
        'id': 68, 'language': 'fr', 'category': 'finance_performance',
        'source_type': 'verified',
        'text': "Le ROI de notre engagement avec ce cabinet a été clairement démontrable : réduction des coûts opérationnels de 18% en 18 mois, amélioration de la satisfaction client de 22 points NPS. Les honoraires élevés sont justifiés quand les résultats sont au rendez-vous et mesurables."
    },
    {
        'id': 69, 'language': 'en', 'category': 'finance_performance',
        'source_type': 'verified',
        'text': "The engagement delivered clear financial returns: we reduced our supply chain costs by 23% and improved working capital by $50M. The fees were significant but the ROI was unambiguous. Good consulting pays for itself many times over when the recommendations are actually implemented."
    },

    # ─────────────────────────────────────────────────────────
    # CATÉGORIE 6 : PARTENARIAT ET STRATÉGIE (12 textes)
    # ─────────────────────────────────────────────────────────
    {
        'id': 70, 'language': 'fr', 'category': 'partenariat_strategie',
        'source_type': 'press',
        'text': "L'annonce du partenariat stratégique entre Capgemini et Google Cloud soulève des questions sur les conflits d'intérêts potentiels. Capgemini conseillera-t-il objectivement ses clients sur le choix des solutions cloud alors qu'il est lié commercialement à Google ? La transparence sur ces partenariats devient indispensable."
    },
    {
        'id': 71, 'language': 'en', 'category': 'partenariat_strategie',
        'source_type': 'press',
        'text': "The merger between two major consulting firms has created the largest advisory practice in Europe. Analysts see significant synergies in digital services and ESG consulting but warn of integration risks and potential client conflicts given the combined firm's dominant market position in several sectors."
    },
    {
        'id': 72, 'language': 'ar', 'category': 'partenariat_strategie',
        'source_type': 'press',
        'text': "إعلان الاندماج بين شركتي استشارات كبريين يعيد رسم خريطة القطاع في المنطقة. الصفقة تُقيَّم بمليار دولار وتخلق كياناً استشارياً بعشرة آلاف موظف. المنافسون يترقبون بقلق بينما يرحب العملاء بتوسع قدرات الخدمة لكنهم يخشون ارتفاع الأسعار."
    },
    {
        'id': 73, 'language': 'de', 'category': 'partenariat_strategie',
        'source_type': 'press',
        'text': "Die strategische Partnerschaft zwischen einem führenden Beratungsunternehmen und einem KI-Startup verspricht revolutionäre Beratungsansätze. Kritiker warnen jedoch vor den Risiken: Datenschutzbedenken beim Einsatz von KI in der Unternehmensberatung und die Frage, wem die generierten Erkenntnisse gehören."
    },
    {
        'id': 74, 'language': 'es', 'category': 'partenariat_strategie',
        'source_type': 'press',
        'text': "La alianza estratégica entre la firma de consultoría y el banco de inversión crea un nuevo modelo de asesoramiento integrado que combina consultoría estratégica con capacidades de financiación. El mercado reacciona positivamente aunque algunos clientes expresan preocupación por posibles conflictos de interés."
    },
    {
        'id': 75, 'language': 'fr', 'category': 'partenariat_strategie',
        'source_type': 'social',
        'text': "Avant de s'associer avec un cabinet de conseil, vérifiez bien leurs partenariats commerciaux. Un cabinet partenaire d'un éditeur logiciel vous recommandera toujours leurs solutions même si ce n'est pas la meilleure option pour vous. L'indépendance du conseil est une valeur qui disparaît progressivement."
    },
    {
        'id': 76, 'language': 'en', 'category': 'partenariat_strategie',
        'source_type': 'social',
        'text': "Before signing with any consulting firm, always ask who their technology and commercial partners are. A firm that has a revenue-sharing agreement with a specific software vendor will always recommend that vendor's products. True independence in consulting advice is increasingly rare and valuable."
    },
    {
        'id': 77, 'language': 'ar', 'category': 'partenariat_strategie',
        'source_type': 'social',
        'text': "قبل التعاقد مع أي شركة استشارات، اسألوا دائماً عن شراكاتهم التجارية وتحالفاتهم الاستراتيجية. الاستشاري الحقيقي يقدم لك أفضل حل لمشكلتك، ليس الحل الذي يجلب له عمولة من شريكه التجاري. الاستقلالية التامة هي معيار التميز الحقيقي في هذا القطاع."
    },
    {
        'id': 78, 'language': 'de', 'category': 'partenariat_strategie',
        'source_type': 'verified',
        'text': "Wir haben bewusst eine Beratungsfirma ohne Technologiepartnerschaften gewählt, um eine unabhängige Empfehlung zu erhalten. Die Qualität der Analyse war hervorragend und die Empfehlungen wirkten nicht von kommerziellen Interessen beeinflusst. Für strategische Entscheidungen ist echte Unabhängigkeit unbezahlbar."
    },
    {
        'id': 79, 'language': 'es', 'category': 'partenariat_strategie',
        'source_type': 'verified',
        'text': "Seleccionamos esta firma precisamente porque no tenía acuerdos comerciales con proveedores tecnológicos, garantizando así una recomendación verdaderamente objetiva. Su análisis fue imparcial y nos permitió tomar una decisión de inversión de 20 millones con plena confianza en la independencia del asesoramiento."
    },
    {
        'id': 80, 'language': 'fr', 'category': 'partenariat_strategie',
        'source_type': 'press',
        'text': "Le rachat de la boutique de conseil spécialisée en cybersécurité par un grand cabinet généraliste soulève des inquiétudes parmi les clients. La spécialisation et l'agilité qui faisaient la force de la boutique survivront-elles à l'intégration dans une grande structure ? L'histoire du secteur montre des résultats mitigés."
    },
    {
        'id': 81, 'language': 'en', 'category': 'partenariat_strategie',
        'source_type': 'press',
        'text': "Due diligence on potential consulting partnerships should include thorough reputation checks. Several companies have discovered too late that their chosen advisory partner had undisclosed relationships with competitors or regulatory issues that significantly compromised the independence of the advice received."
    },

    # ─────────────────────────────────────────────────────────
    # CATÉGORIE 7 : INNOVATION ET TECHNOLOGIE (9 textes)
    # ─────────────────────────────────────────────────────────
    {
        'id': 82, 'language': 'fr', 'category': 'innovation_tech',
        'source_type': 'press',
        'text': "Les cabinets de conseil investissent massivement dans l'intelligence artificielle pour automatiser les tâches d'analyse et améliorer la qualité de leurs livrables. McKinsey a créé une division IA de 1000 personnes. La question reste entière : cette technologisation va-t-elle améliorer les conseils ou simplement réduire les coûts en remplaçant les juniors ?"
    },
    {
        'id': 83, 'language': 'en', 'category': 'innovation_tech',
        'source_type': 'press',
        'text': "AI is disrupting the consulting industry in profound ways. Tools that can analyze thousands of documents in minutes are replacing weeks of junior analyst work. The firms that will thrive are those that can combine AI efficiency with human judgment and client relationship skills that technology cannot replicate."
    },
    {
        'id': 84, 'language': 'ar', 'category': 'innovation_tech',
        'source_type': 'press',
        'text': "الذكاء الاصطناعي يعيد تشكيل صناعة الاستشارات بشكل جذري. الشركات الكبرى تستثمر مليارات الدولارات في تطوير أدوات تحليلية متقدمة تُمكّن المستشارين من تقديم رؤى أعمق وأسرع. لكن الخبراء يتساءلون: هل سيحل الذكاء الاصطناعي محل المستشار البشري أم سيعززه؟"
    },
    {
        'id': 85, 'language': 'de', 'category': 'innovation_tech',
        'source_type': 'press',
        'text': "Generative KI verändert die Beratungsbranche fundamental. Analysen, für die früher Teams von Junior-Beratern wochenlang arbeiteten, lassen sich nun in Stunden durchführen. Die Herausforderung liegt darin, die Effizienzgewinne an die Kunden weiterzugeben ohne die eigene Profitabilität zu gefährden."
    },
    {
        'id': 86, 'language': 'es', 'category': 'innovation_tech',
        'source_type': 'press',
        'text': "La inteligencia artificial generativa está transformando los modelos de negocio de las consultoras. Las firmas que lideren esta transición podrán ofrecer análisis más profundos a menor costo, pero enfrentarán la paradoja de destruir su propio modelo basado en horas facturables de trabajo humano."
    },
    {
        'id': 87, 'language': 'fr', 'category': 'innovation_tech',
        'source_type': 'social',
        'text': "J'ai demandé à ChatGPT de faire une analyse stratégique de mon secteur et le résultat était franchement comparable à ce que j'ai payé 50k€ à un cabinet il y a 3 ans. L'IA va complètement disrupter les cabinets de conseil dans les 5 prochaines années. Ceux qui ne s'adaptent pas vont mourir."
    },
    {
        'id': 88, 'language': 'en', 'category': 'innovation_tech',
        'source_type': 'social',
        'text': "The consulting industry's dirty secret: a significant portion of what they charge premium fees for can now be done by AI tools in minutes. The firms know this. That's why they're all rushing to acquire AI capabilities and reposition as AI implementation partners before their core business erodes."
    },
    {
        'id': 89, 'language': 'ar', 'category': 'innovation_tech',
        'source_type': 'social',
        'text': "استخدمت أدوات الذكاء الاصطناعي لتحليل السوق وجاءت النتائج مماثلة لما دفعت فيه الآلاف لشركة استشارات. هذا لا يعني أن الاستشاريين لا قيمة لهم، لكنه يعيد تحديد قيمتهم الحقيقية في الحكم والخبرة والعلاقات، لا في التحليل الروتيني الذي يمكن للآلة إنجازه."
    },
    {
        'id': 90, 'language': 'de', 'category': 'innovation_tech',
        'source_type': 'verified',
        'text': "Das Beratungsunternehmen nutzte KI-Tools, um unsere Marktdaten in Echtzeit zu analysieren und Muster zu identifizieren, die menschliche Analysten übersehen hätten. Das Ergebnis war beeindruckend: tiefere Einblicke in kürzerer Zeit. KI macht gute Berater besser, ersetzt sie aber nicht."
    },

    # ─────────────────────────────────────────────────────────
    # CATÉGORIE 8 : RSE ET ÉTHIQUE (10 textes)
    # ─────────────────────────────────────────────────────────
    {
        'id': 91, 'language': 'fr', 'category': 'rse_ethique',
        'source_type': 'press',
        'text': "Le rapport RSE de KPMG sur les pratiques durables des entreprises mondiales est une référence annuelle très attendue. L'édition de cette année révèle que 96% des plus grandes entreprises publient désormais des rapports de durabilité mais que la qualité et la vérifiabilité des données restent très hétérogènes."
    },
    {
        'id': 92, 'language': 'en', 'category': 'rse_ethique',
        'source_type': 'press',
        'text': "Consulting firms face growing scrutiny over their ESG credentials given the nature of their client base. How can a firm credibly advise on sustainability while simultaneously serving oil companies, tobacco firms and controversial industries? The tension between commercial interests and ethical positioning is becoming unsustainable."
    },
    {
        'id': 93, 'language': 'ar', 'category': 'rse_ethique',
        'source_type': 'press',
        'text': "مسؤولية الشركات الاجتماعية في قطاع الاستشارات تحت المجهر. شركات تتحدث عن الاستدامة وأخلاقيات الأعمال بينما تقدم خدماتها لعملاء في قطاعات مثيرة للجدل. الفجوة بين الخطاب والممارسة تؤثر على مصداقية هذه الشركات ويجب معالجتها بشفافية."
    },
    {
        'id': 94, 'language': 'de', 'category': 'rse_ethique',
        'source_type': 'press',
        'text': "Unternehmensberater werden zunehmend für ihre Rolle bei Entscheidungen mit weitreichenden gesellschaftlichen Konsequenzen verantwortlich gemacht. Die Branche diskutiert einen ethischen Kodex für Beratungsleistungen, ähnlich dem Hippokratischen Eid in der Medizin. Die Umsetzung bleibt jedoch freiwillig und schwer überprüfbar."
    },
    {
        'id': 95, 'language': 'es', 'category': 'rse_ethique',
        'source_type': 'press',
        'text': "El sector de consultoría debate la necesidad de estándares éticos obligatorios tras varios escándalos que revelaron asesoramiento irresponsable con graves consecuencias sociales. La autorregulación ha demostrado ser insuficiente y los reguladores europeos estudian introducir requisitos de responsabilidad profesional más estrictos."
    },
    {
        'id': 96, 'language': 'fr', 'category': 'rse_ethique',
        'source_type': 'social',
        'text': "Un cabinet de conseil qui parle de RSE le matin et aide ses clients à optimiser leurs impôts de façon agressive l'après-midi, c'est de l'hypocrisie pure. L'éthique en conseil ne peut pas être un argument marketing, elle doit être une contrainte opérationnelle réelle avec des mécanismes de sanction."
    },
    {
        'id': 97, 'language': 'en', 'category': 'rse_ethique',
        'source_type': 'social',
        'text': "Consulting firms publishing beautiful ESG reports while advising clients on aggressive tax avoidance is the definition of greenwashing. The industry needs mandatory ethical standards, not voluntary codes of conduct that are conveniently ignored when they conflict with revenue generation."
    },
    {
        'id': 98, 'language': 'ar', 'category': 'rse_ethique',
        'source_type': 'social',
        'text': "شركات الاستشارات التي تُسوّق نفسها على أنها مسؤولة اجتماعياً بينما تساعد عملاءها على التهرب الضريبي وتجاوز اللوائح البيئية تمارس نوعاً من الغسيل الأخضر الخطير. المصداقية تتطلب توافقاً حقيقياً بين الخطاب والفعل، لا مجرد تقارير براقة للعلاقات العامة."
    },
    {
        'id': 99, 'language': 'de', 'category': 'rse_ethique',
        'source_type': 'verified',
        'text': "Wir haben die Nachhaltigkeitsstrategie unseres Unternehmens gemeinsam mit dem Beratungsunternehmen entwickelt. Das Team war in Bezug auf ethische Fragen überraschend klar: Sie lehnten Empfehlungen ab, die zwar legal, aber gesellschaftlich problematisch gewesen wären. Diese Haltung hat unser Vertrauen in sie gestärkt."
    },
    {
        'id': 100, 'language': 'es', 'category': 'rse_ethique',
        'source_type': 'verified',
        'text': "La firma de consultoría nos asesoró sobre nuestra estrategia de sostenibilidad con un enfoque genuinamente ético. Rechazaron varias opciones que habrían maximizado los beneficios a corto plazo pero comprometido nuestra reputación a largo plazo. Esa independencia y visión a largo plazo es lo que diferencia a los verdaderos asesores estratégicos."
    },
]


def get_corpus():
    return CORPUS_KPMG


def get_corpus_by_category(category: str):
    return [item for item in CORPUS_KPMG if item['category'] == category]


def get_corpus_by_language(language: str):
    return [item for item in CORPUS_KPMG if item['language'] == language]


def get_corpus_by_source(source_type: str):
    return [item for item in CORPUS_KPMG if item['source_type'] == source_type]


def get_corpus_statistics():
    from collections import Counter
    return {
        'total': len(CORPUS_KPMG),
        'by_category': dict(Counter(item['category'] for item in CORPUS_KPMG)),
        'by_language': dict(Counter(item['language'] for item in CORPUS_KPMG)),
        'by_source': dict(Counter(item['source_type'] for item in CORPUS_KPMG)),
    }


if __name__ == "__main__":
    stats = get_corpus_statistics()
    print("=" * 60)
    print("STATISTIQUES DU CORPUS KPMG DUE DILIGENCE")
    print("=" * 60)
    print(f"\nTotal documents  : {stats['total']}")
    print(f"\nPar catégorie    : ")
    for cat, count in stats['by_category'].items():
        print(f"  {cat:<25} : {count}")
    print(f"\nPar langue       : {stats['by_language']}")
    print(f"\nPar source       : {stats['by_source']}")