"""Internationalization (i18n) module for llmCli with multi-language support.

Supported languages:
- pt-BR: Português (Brasil)
- en-US: English (US)
- es-ES: Español
- de-DE: Deutsch (Alemão)
- fr-FR: Français (Francês)
- zh-CN: 简体中文 (Chinês)
- ru-RU: Русский (Russo)
- hi-IN: हिन्दी (Hindi / Indiano)
- auto: Detecção automática via SO / locale
"""
from __future__ import annotations

import locale
import os
from typing import Dict, Any, Optional

SUPPORTED_LANGUAGES = {
    "pt-BR": {"name": "Português (Brasil)", "flag": "🇧🇷"},
    "en-US": {"name": "English (US)", "flag": "🇺🇸"},
    "es-ES": {"name": "Español", "flag": "🇪🇸"},
    "de-DE": {"name": "Deutsch", "flag": "🇩🇪"},
    "fr-FR": {"name": "Français", "flag": "🇫🇷"},
    "zh-CN": {"name": "简体中文", "flag": "🇨🇳"},
    "ru-RU": {"name": "Русский", "flag": "🇷🇺"},
    "hi-IN": {"name": "हिन्दी (Hindi)", "flag": "🇮🇳"}
}

LANGUAGE_ALIASES = {
    # Português
    "pt": "pt-BR", "pt-br": "pt-BR", "pt_br": "pt-BR", "portugues": "pt-BR", "portuguese": "pt-BR",
    # Inglês
    "en": "en-US", "en-us": "en-US", "en_us": "en-US", "ingles": "en-US", "english": "en-US",
    # Espanhol
    "es": "es-ES", "es-es": "es-ES", "es_es": "es-ES", "espanhol": "es-ES", "spanish": "es-ES",
    # Alemão
    "de": "de-DE", "de-de": "de-DE", "de_de": "de-DE", "alemao": "de-DE", "german": "de-DE", "deutsch": "de-DE",
    # Francês
    "fr": "fr-FR", "fr-fr": "fr-FR", "fr_fr": "fr-FR", "frances": "fr-FR", "french": "fr-FR", "francais": "fr-FR",
    # Chinês
    "zh": "zh-CN", "zh-cn": "zh-CN", "zh_cn": "zh-CN", "chines": "zh-CN", "chinese": "zh-CN", "mandarin": "zh-CN",
    # Russo
    "ru": "ru-RU", "ru-ru": "ru-RU", "ru_ru": "ru-RU", "russo": "ru-RU", "russian": "ru-RU",
    # Hindi / Indiano
    "hi": "hi-IN", "hi-in": "hi-IN", "hi_in": "hi-IN", "indiano": "hi-IN", "hindi": "hi-IN", "indian": "hi-IN",
    # Auto
    "auto": "auto", "default": "auto"
}

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "pt-BR": {
        "banner_subtitle": "llmCli - Assistente IA de Código Híbrido (Local & Nuvem)",
        "banner_desc": "Suporte nativo a llama.cpp (porta 8080), Ollama, LM Studio, vLLM, Gemini, OpenAI, Anthropic e DeepSeek.\nDigite /help para ver comandos ou /yolo para alternar o modo autônomo.",
        "yolo_on": "⚡ MODO YOLO ATIVADO para {model} (preferência salva)!",
        "yolo_off": "🛡️ MODO YOLO DESATIVADO para {model} (preferência salva).",
        "model_switched": "✓ Modelo ativo alterado para: {model}",
        "arch_on": "🏛️ MODO ARQUITETO ATIVADO: Arquiteto: {arch} | Editor: {editor}",
        "arch_off": "🛡️ MODO ARQUITETO DESATIVADO: Usando modelo único padrão.",
        "arch_planning": "🏛️ [Arquiteto: {arch}] Planejando solução...",
        "arch_applying": "⚡ [Editor: {editor}] Aplicando alterações nos arquivos...",
        "confirm_tool": "Deseja executar a ferramenta '{tool}' com os argumentos: {args}?",
        "confirm_editor": "Deseja que o Editor ({editor}) aplique o plano nos arquivos?",
        "confirm_commit": "Deseja criar o commit com esta mensagem?",
        "commit_success": "Commit criado com sucesso [{hash}]: {msg}",
        "commit_suggested": "Mensagem de commit sugerida:",
        "commit_no_diff": "Nenhuma alteração Git não commitada encontrada para gerar commit.",
        "review_no_diff": "Nenhuma alteração Git detectada para Code Review.",
        "review_running": "Executando Code Review nas alterações Git pendentes...",
        "compact_success": "✓ Histórico compactado com sucesso! Estimativa atual: ~{tokens} tokens",
        "compact_empty": "Histórico da conversa está vazio, nada a compactar.",
        "temp_current": "Temperatura atual para {model}: {temp} (padrão: 0.2)",
        "temp_changed": "✓ Temperatura para {model} alterada para: {temp} (preferência salva)",
        "temp_invalid": "Valor de temperatura inválido. Use um número float entre 0.0 e 2.0.",
        "sys_current": "System Prompt Ativo:\n{prompt}",
        "sys_reset": "System prompt redefinido para o padrão com sucesso.",
        "sys_custom": "✓ System prompt personalizado configurado para esta sessão.",
        "paste_active": "📋 Modo Multilinha ativado. Digite ':done' em uma linha para enviar ou ':cancel' para abortar.",
        "paste_cancel": "Modo multilinha cancelado.",
        "session_reset": "Sessão reiniciada (histórico e arquivos limpos).",
        "prefs_reset": "✓ Todas as preferências salvas (globais e por LLM) foram redefinidas para o padrão.",
        "all_reset": "✓ Sessão e preferências de usuário totalmente reiniciadas para o padrão.",
        "lang_current": "Idioma ativo: {flag} {name} ({code})",
        "lang_changed": "✓ Idioma alterado com sucesso para: {flag} {name} ({code})",
        "exit_msg": "Encerrando llmCli. Até logo!",
        "unknown_cmd": "Comando desconhecido: '{cmd}'. Digite /help para ver os comandos disponíveis.",
        "ambiguous_cmd": "Comando ambíguo '{cmd}'. Opções possíveis: {options}",
        "prompt_ai_instruction": "Responda sempre em Português do Brasil com explicações claras e código bem documentado."
    },
    "en-US": {
        "banner_subtitle": "llmCli - Hybrid AI Coding Assistant (Local & Cloud)",
        "banner_desc": "Native support for llama.cpp (port 8080), Ollama, LM Studio, vLLM, Gemini, OpenAI, Anthropic, and DeepSeek.\nType /help to see commands or /yolo to toggle autonomous mode.",
        "yolo_on": "⚡ YOLO MODE ENABLED for {model} (preference saved)!",
        "yolo_off": "🛡️ YOLO MODE DISABLED for {model} (preference saved).",
        "model_switched": "✓ Active model switched to: {model}",
        "arch_on": "🏛️ ARCHITECT MODE ENABLED: Architect: {arch} | Editor: {editor}",
        "arch_off": "🛡️ ARCHITECT MODE DISABLED: Using single default model.",
        "arch_planning": "🏛️ [Architect: {arch}] Planning solution...",
        "arch_applying": "⚡ [Editor: {editor}] Applying changes to files...",
        "confirm_tool": "Execute tool '{tool}' with arguments: {args}?",
        "confirm_editor": "Apply the plan to files using Editor ({editor})?",
        "confirm_commit": "Create commit with this message?",
        "commit_success": "Commit successfully created [{hash}]: {msg}",
        "commit_suggested": "Suggested commit message:",
        "commit_no_diff": "No uncommitted Git changes found to generate a commit.",
        "review_no_diff": "No Git changes detected for Code Review.",
        "review_running": "Running Code Review on pending Git changes...",
        "compact_success": "✓ History compacted successfully! Current estimate: ~{tokens} tokens",
        "compact_empty": "Conversation history is empty, nothing to compact.",
        "temp_current": "Current temperature for {model}: {temp} (default: 0.2)",
        "temp_changed": "✓ Temperature for {model} changed to: {temp} (preference saved)",
        "temp_invalid": "Invalid temperature value. Use a float between 0.0 and 2.0.",
        "sys_current": "Active System Prompt:\n{prompt}",
        "sys_reset": "System prompt reset to default successfully.",
        "sys_custom": "✓ Custom system prompt configured for this session.",
        "paste_active": "📋 Multiline Mode active. Type ':done' on a line to submit or ':cancel' to abort.",
        "paste_cancel": "Multiline mode canceled.",
        "session_reset": "Session reset (history and tracked files cleared).",
        "prefs_reset": "✓ All saved preferences (global and per-LLM) have been reset to default.",
        "all_reset": "✓ Session and user preferences fully reset to default.",
        "lang_current": "Active language: {flag} {name} ({code})",
        "lang_changed": "✓ Language successfully changed to: {flag} {name} ({code})",
        "exit_msg": "Exiting llmCli. Goodbye!",
        "unknown_cmd": "Unknown command: '{cmd}'. Type /help to see available commands.",
        "ambiguous_cmd": "Ambiguous command '{cmd}'. Possible matches: {options}",
        "prompt_ai_instruction": "Always respond in English with clear explanations and well-structured code."
    },
    "es-ES": {
        "banner_subtitle": "llmCli - Asistente de IA para Código Híbrido (Local y Nube)",
        "banner_desc": "Soporte nativo para llama.cpp (puerto 8080), Ollama, LM Studio, vLLM, Gemini, OpenAI, Anthropic y DeepSeek.\nEscribe /help para ver comandos o /yolo para alternar modo autónomo.",
        "yolo_on": "⚡ MODO YOLO ACTIVADO para {model} (preferencia guardada)!",
        "yolo_off": "🛡️ MODO YOLO DESACTIVADO para {model} (preferencia guardada).",
        "model_switched": "✓ Modelo activo cambiado a: {model}",
        "arch_on": "🏛️ MODO ARQUITECTO ACTIVADO: Arquitecto: {arch} | Editor: {editor}",
        "arch_off": "🛡️ MODO ARQUITECTO DESACTIVADO: Usando modelo único estándar.",
        "arch_planning": "🏛️ [Arquitecto: {arch}] Planificando solución...",
        "arch_applying": "⚡ [Editor: {editor}] Aplicando cambios en archivos...",
        "confirm_tool": "¿Ejecutar herramienta '{tool}' con argumentos: {args}?",
        "confirm_editor": "¿Aplicar el plan en los archivos usando el Editor ({editor})?",
        "confirm_commit": "¿Crear commit con este mensaje?",
        "commit_success": "Commit creado con éxito [{hash}]: {msg}",
        "commit_suggested": "Mensaje de commit sugerido:",
        "commit_no_diff": "No se encontraron cambios Git sin confirmar.",
        "review_no_diff": "No se detectaron cambios Git para Code Review.",
        "review_running": "Ejecutando Code Review en cambios Git pendientes...",
        "compact_success": "✓ ¡Historial compactado con éxito! Estimación actual: ~{tokens} tokens",
        "compact_empty": "El historial de conversación está vacío, nada que compactar.",
        "temp_current": "Temperatura actual para {model}: {temp} (predeterminada: 0.2)",
        "temp_changed": "✓ Temperatura para {model} cambiada a: {temp} (preferencia guardada)",
        "temp_invalid": "Valor de temperatura inválido. Use un número flotante entre 0.0 y 2.0.",
        "sys_current": "System Prompt Activo:\n{prompt}",
        "sys_reset": "System prompt restablecido a los valores predeterminados.",
        "sys_custom": "✓ System prompt personalizado configurado para esta sesión.",
        "paste_active": "📋 Modo Multilínea activado. Escriba ':done' para enviar o ':cancel' para cancelar.",
        "paste_cancel": "Modo multilínea cancelado.",
        "session_reset": "Sesión reiniciada (historial y archivos limpios).",
        "prefs_reset": "✓ Todas las preferencias guardadas han sido restablecidas.",
        "all_reset": "✓ Sesión y preferencias totalmente restablecidas.",
        "lang_current": "Idioma activo: {flag} {name} ({code})",
        "lang_changed": "✓ Idioma cambiado con éxito a: {flag} {name} ({code})",
        "exit_msg": "¡Cerrando llmCli. Hasta pronto!",
        "unknown_cmd": "Comando desconocido: '{cmd}'. Escriba /help para ver los comandos.",
        "ambiguous_cmd": "Comando ambiguo '{cmd}'. Opciones: {options}",
        "prompt_ai_instruction": "Responda siempre en Español con explicaciones claras y código bien documentado."
    },
    "de-DE": {
        "banner_subtitle": "llmCli - Hybrider KI-Programmierassistent (Lokal & Cloud)",
        "banner_desc": "Native Unterstützung für llama.cpp (Port 8080), Ollama, LM Studio, vLLM, Gemini, OpenAI, Anthropic und DeepSeek.\nTippen Sie /help für Befehle oder /yolo für den autonomen Modus.",
        "yolo_on": "⚡ YOLO-MODUS AKTIVIERT für {model} (Einstellung gespeichert)!",
        "yolo_off": "🛡️ YOLO-MODUS DEAKTIVIERT für {model} (Einstellung gespeichert).",
        "model_switched": "✓ Aktives Modell gewechselt zu: {model}",
        "arch_on": "🏛️ ARCHITEKTENMODUS AKTIVIERT: Architekt: {arch} | Editor: {editor}",
        "arch_off": "🛡️ ARCHITEKTENMODUS DEAKTIVIERT: Standardmodell aktiv.",
        "arch_planning": "🏛️ [Architekt: {arch}] Lösung wird geplant...",
        "arch_applying": "⚡ [Editor: {editor}] Änderungen werden angewendet...",
        "confirm_tool": "Werkzeug '{tool}' mit Argumenten ausführen: {args}?",
        "confirm_editor": "Plan mit Editor ({editor}) auf Dateien anwenden?",
        "confirm_commit": "Commit mit dieser Nachricht erstellen?",
        "commit_success": "Commit erfolgreich erstellt [{hash}]: {msg}",
        "commit_suggested": "Vorgeschlagene Commit-Nachricht:",
        "commit_no_diff": "Keine ungespeicherten Git-Änderungen gefunden.",
        "review_no_diff": "Keine Git-Änderungen für Code Review vorhanden.",
        "review_running": "Code Review für ausstehende Git-Änderungen läuft...",
        "compact_success": "✓ Verlauf erfolgreich komprimiert! Schätzung: ~{tokens} Tokens",
        "compact_empty": "Gesprächsverlauf ist leer, nichts zu komprimieren.",
        "temp_current": "Aktuelle Temperatur für {model}: {temp} (Standard: 0.2)",
        "temp_changed": "✓ Temperatur für {model} geändert auf: {temp} (gespeichert)",
        "temp_invalid": "Ungültige Temperatur. Bitte Zahl zwischen 0.0 und 2.0 eingeben.",
        "sys_current": "Aktiver System-Prompt:\n{prompt}",
        "sys_reset": "System-Prompt erfolgreich auf Standard zurückgesetzt.",
        "sys_custom": "✓ Benutzerdefinierter System-Prompt für diese Sitzung aktiv.",
        "paste_active": "📋 Mehrzeilen-Modus aktiv. ':done' zum Senden oder ':cancel' zum Abbrechen.",
        "paste_cancel": "Mehrzeilen-Modus abgebrochen.",
        "session_reset": "Sitzung zurückgesetzt (Verlauf und Dateien gelöscht).",
        "prefs_reset": "✓ Alle Einstellungen auf Standardwerte zurückgesetzt.",
        "all_reset": "✓ Sitzung und Einstellungen vollständig zurückgesetzt.",
        "lang_current": "Aktive Sprache: {flag} {name} ({code})",
        "lang_changed": "✓ Sprache erfolgreich geändert auf: {flag} {name} ({code})",
        "exit_msg": "llmCli wird beendet. Auf Wiedersehen!",
        "unknown_cmd": "Unbekannter Befehl: '{cmd}'. Geben Sie /help ein.",
        "ambiguous_cmd": "Mehrdeutiger Befehl '{cmd}'. Optionen: {options}",
        "prompt_ai_instruction": "Antworten Sie immer auf Deutsch mit klaren Erklärungen und sauberem Code."
    },
    "fr-FR": {
        "banner_subtitle": "llmCli - Assistant IA de Code Hybride (Local & Cloud)",
        "banner_desc": "Support natif de llama.cpp (port 8080), Ollama, LM Studio, vLLM, Gemini, OpenAI, Anthropic et DeepSeek.\nTapez /help pour les commandes ou /yolo pour le mode autonome.",
        "yolo_on": "⚡ MODE YOLO ACTIVÉ pour {model} (préférence enregistrée) !",
        "yolo_off": "🛡️ MODE YOLO DÉSACTIVÉ pour {model} (préférence enregistrée).",
        "model_switched": "✓ Modèle actif changé pour : {model}",
        "arch_on": "🏛️ MODE ARCHITECTE ACTIVÉ : Architecte : {arch} | Éditeur : {editor}",
        "arch_off": "🛡️ MODE ARCHITECTE DÉSACTIVÉ : Modèle standard actif.",
        "arch_planning": "🏛️ [Architecte : {arch}] Planification de la solution...",
        "arch_applying": "⚡ [Éditeur : {editor}] Application des modifications...",
        "confirm_tool": "Exécuter l'outil '{tool}' avec les arguments : {args} ?",
        "confirm_editor": "Appliquer le plan aux fichiers avec l'Éditeur ({editor}) ?",
        "confirm_commit": "Créer le commit avec ce message ?",
        "commit_success": "Commit créé avec succès [{hash}] : {msg}",
        "commit_suggested": "Message de commit suggéré :",
        "commit_no_diff": "Aucune modification Git non commitée trouvée.",
        "review_no_diff": "Aucune modification Git détectée pour la revue de code.",
        "review_running": "Revue de code en cours sur les modifications Git...",
        "compact_success": "✓ Historique compacté avec succès ! Estimation : ~{tokens} tokens",
        "compact_empty": "L'historique de conversation est vide.",
        "temp_current": "Température actuelle pour {model} : {temp} (défaut : 0.2)",
        "temp_changed": "✓ Température pour {model} changée à : {temp} (enregistrée)",
        "temp_invalid": "Température invalide. Utilisez un nombre entre 0.0 et 2.0.",
        "sys_current": "System Prompt Actif :\n{prompt}",
        "sys_reset": "System prompt réinitialisé par défaut.",
        "sys_custom": "✓ System prompt personnalisé configuré pour cette session.",
        "paste_active": "📋 Mode multiligne actif. Tapez ':done' pour envoyer ou ':cancel' pour annuler.",
        "paste_cancel": "Mode multiligne annulé.",
        "session_reset": "Session réinitialisée (historique et fichiers effacés).",
        "prefs_reset": "✓ Toutes les préférences ont été réinitialisées par défaut.",
        "all_reset": "✓ Session et préférences entièrement réinitialisées.",
        "lang_current": "Langue active : {flag} {name} ({code})",
        "lang_changed": "✓ Langue changée avec succès pour : {flag} {name} ({code})",
        "exit_msg": "Fermeture de llmCli. Au revoir !",
        "unknown_cmd": "Commande inconnue : '{cmd}'. Tapez /help.",
        "ambiguous_cmd": "Commande ambiguë '{cmd}'. Options possibles : {options}",
        "prompt_ai_instruction": "Répondez toujours en Français avec des explications claires et du code propre."
    },
    "zh-CN": {
        "banner_subtitle": "llmCli - 混合AI代码助手 (本地 & 云端)",
        "banner_desc": "原生支持 llama.cpp (端口 8080), Ollama, LM Studio, vLLM, Gemini, OpenAI, Anthropic 和 DeepSeek。\n输入 /help 查看命令或 /yolo 切换自主模式。",
        "yolo_on": "⚡ 已为 {model} 开启 YOLO 模式 (偏好已保存)！",
        "yolo_off": "🛡️ 已为 {model} 关闭 YOLO 模式 (偏好已保存)。",
        "model_switched": "✓ 当前模型已切换为：{model}",
        "arch_on": "🏛️ 架构师模式已开启：架构师：{arch} | 编辑器：{editor}",
        "arch_off": "🛡️ 架构师模式已关闭：使用默认单一模型。",
        "arch_planning": "🏛️ [架构师：{arch}] 正在规划方案...",
        "arch_applying": "⚡ [编辑器：{editor}] 正在应用文件更改...",
        "confirm_tool": "是否执行工具 '{tool}'，参数为：{args}？",
        "confirm_editor": "是否让编辑器 ({editor}) 将方案应用到文件中？",
        "confirm_commit": "是否使用此信息创建提交？",
        "commit_success": "提交创建成功 [{hash}]: {msg}",
        "commit_suggested": "建议的提交信息：",
        "commit_no_diff": "未发现未提交的 Git 更改。",
        "review_no_diff": "未检测到需要代码审查的 Git 更改。",
        "review_running": "正在对待处理的 Git 更改进行代码审查...",
        "compact_success": "✓ 历史记录压缩成功！当前预估：~{tokens} tokens",
        "compact_empty": "对话历史为空，无需压缩。",
        "temp_current": "{model} 当前温度：{temp} (默认：0.2)",
        "temp_changed": "✓ {model} 温度已更改为：{temp} (已保存)",
        "temp_invalid": "温度值无效。请输入 0.0 到 2.0 之间的浮点数。",
        "sys_current": "当前系统提示词：\n{prompt}",
        "sys_reset": "系统提示词已成功重置为默认值。",
        "sys_custom": "✓ 已为此会话配置自定义系统提示词。",
        "paste_active": "📋 多行模式已激活。单行输入 ':done' 提交，输入 ':cancel' 取消。",
        "paste_cancel": "多行模式已取消。",
        "session_reset": "会话已重置 (历史记录和文件已清空)。",
        "prefs_reset": "✓ 所有保存的偏好设置已重置为默认值。",
        "all_reset": "✓ 会话和偏好设置已全部重置。",
        "lang_current": "当前语言：{flag} {name} ({code})",
        "lang_changed": "✓ 语言已成功更改为：{flag} {name} ({code})",
        "exit_msg": "正在退出 llmCli。再见！",
        "unknown_cmd": "未知命令：'{cmd}'。输入 /help 查看可用命令。",
        "ambiguous_cmd": "命令歧义 '{cmd}'。可用选项：{options}",
        "prompt_ai_instruction": "请始终用简体中文回答，提供清晰的解释和规范的代码。"
    },
    "ru-RU": {
        "banner_subtitle": "llmCli - Гибридный ИИ-ассистент для разработки (Локальный и Облачный)",
        "banner_desc": "Нативная поддержка llama.cpp (порт 8080), Ollama, LM Studio, vLLM, Gemini, OpenAI, Anthropic и DeepSeek.\nВведите /help для команд или /yolo для переключения автономного режима.",
        "yolo_on": "⚡ РЕЖИМ YOLO ВКЛЮЧЕН для {model} (настройка сохранена)!",
        "yolo_off": "🛡️ РЕЖИМ YOLO ВЫКЛЮЧЕН для {model} (настройка сохранена).",
        "model_switched": "✓ Активная модель изменена на: {model}",
        "arch_on": "🏛️ РЕЖИМ АРХИТЕКТОРА ВКЛЮЧЕН: Архитектор: {arch} | Редактор: {editor}",
        "arch_off": "🛡️ РЕЖИМ АРХИТЕКТОРА ВЫКЛЮЧЕН: Используется стандартная модель.",
        "arch_planning": "🏛️ [Архитектор: {arch}] Планирование решения...",
        "arch_applying": "⚡ [Редактор: {editor}] Применение изменений в файлах...",
        "confirm_tool": "Выполнить инструмент '{tool}' с аргументами: {args}?",
        "confirm_editor": "Применить план к файлам с помощью Редактора ({editor})?",
        "confirm_commit": "Создать коммит с этим сообщением?",
        "commit_success": "Коммит успешно создан [{hash}]: {msg}",
        "commit_suggested": "Предложенное сообщение коммита:",
        "commit_no_diff": "Не зафиксированных изменений Git не найдено.",
        "review_no_diff": "Изменений Git для Code Review не обнаружено.",
        "review_running": "Выполняется Code Review ожидающих изменений Git...",
        "compact_success": "✓ История успешно сжата! Текущая оценка: ~{tokens} токенов",
        "compact_empty": "История диалога пуста, сжимать нечего.",
        "temp_current": "Текущая температура для {model}: {temp} (по умолчанию: 0.2)",
        "temp_changed": "✓ Температура для {model} изменена на: {temp} (сохранено)",
        "temp_invalid": "Неверное значение температуры. Введите число от 0.0 до 2.0.",
        "sys_current": "Активный системный промпт:\n{prompt}",
        "sys_reset": "Системный промпт сброшен до стандартного.",
        "sys_custom": "✓ Пользовательский системный промпт настроен для этой сессии.",
        "paste_active": "📋 Многострочный режим активен. Введите ':done' для отправки или ':cancel' для отмены.",
        "paste_cancel": "Многострочный режим отменен.",
        "session_reset": "Сессия сброшена (история и файлы очищены).",
        "prefs_reset": "✓ Все сохраненные настройки сброшены по умолчанию.",
        "all_reset": "✓ Сессия и настройки полностью сброшены.",
        "lang_current": "Активный язык: {flag} {name} ({code})",
        "lang_changed": "✓ Язык успешно изменен на: {flag} {name} ({code})",
        "exit_msg": "Завершение работы llmCli. До свидания!",
        "unknown_cmd": "Неизвестная команда: '{cmd}'. Введите /help.",
        "ambiguous_cmd": "Неоднозначная команда '{cmd}'. Варианты: {options}",
        "prompt_ai_instruction": "Всегда отвечайте на русском языке с понятными объяснениями и чистым кодом."
    },
    "hi-IN": {
        "banner_subtitle": "llmCli - हाइब्रिड AI कोडिंग सहायक (स्थानीय और क्लाउड)",
        "banner_desc": "llama.cpp (पोर्ट 8080), Ollama, LM Studio, vLLM, Gemini, OpenAI, Anthropic और DeepSeek के लिए मूल समर्थन।\nकमांड के लिए /help या स्वायत्त मोड के लिए /yolo टाइप करें।",
        "yolo_on": "⚡ {model} के लिए YOLO मोड सक्षम (प्राथमिकता सहेजी गई)!",
        "yolo_off": "🛡️ {model} के लिए YOLO मोड अक्षम (प्राथमिकता सहेजी गई)।",
        "model_switched": "✓ सक्रिय मॉडल बदलकर {model} कर दिया गया है",
        "arch_on": "🏛️ आर्किटेक्ट मोड सक्षम: आर्किटेक्ट: {arch} | संपादक: {editor}",
        "arch_off": "🛡️ आर्किटेक्ट मोड अक्षम: मानक एकल मॉडल सक्रिय।",
        "arch_planning": "🏛️ [आर्किटेक्ट: {arch}] समाधान की योजना बनाई जा रही है...",
        "arch_applying": "⚡ [संपादक: {editor}] फ़ाइलों में बदलाव लागू किए जा रहे हैं...",
        "confirm_tool": "क्या तर्क {args} के साथ टूल '{tool}' निष्पादित करें?",
        "confirm_editor": "क्या संपादक ({editor}) द्वारा योजना को फ़ाइलों पर लागू करें?",
        "confirm_commit": "क्या इस संदेश के साथ कमिट बनाएं?",
        "commit_success": "कमिट सफलतापूर्वक बनाया गया [{hash}]: {msg}",
        "commit_suggested": "सुझाया गया कमिट संदेश:",
        "commit_no_diff": "कोई गैर-प्रतिबद्ध Git परिवर्तन नहीं मिले।",
        "review_no_diff": "कोड समीक्षा के लिए कोई Git परिवर्तन नहीं मिला।",
        "review_running": "लंबित Git परिवर्तनों पर कोड समीक्षा चल रही है...",
        "compact_success": "✓ इतिहास सफलतापूर्वक संक्षिप्त किया गया! अनुमानित टोकन: ~{tokens}",
        "compact_empty": "बातचीत का इतिहास खाली है।",
        "temp_current": "{model} के लिए वर्तमान तापमान: {temp} (डिफ़ॉल्ट: 0.2)",
        "temp_changed": "✓ {model} का तापमान बदलकर {temp} कर दिया गया (सहेजा गया)",
        "temp_invalid": "अमान्य तापमान मान। 0.0 और 2.0 के बीच एक संख्या दर्ज करें।",
        "sys_current": "सक्रिय सिस्टम प्रॉम्प्ट:\n{prompt}",
        "sys_reset": "सिस्टम प्रॉम्प्ट सफलतापूर्वक डिफ़ॉल्ट पर रीसेट किया गया।",
        "sys_custom": "✓ इस सत्र के लिए कस्टम सिस्टम प्रॉम्प्ट सेट किया गया।",
        "paste_active": "📋 मल्टीलाइन मोड सक्रिय। भेजने के लिए ':done' या रद्द करने के लिए ':cancel' लिखें।",
        "paste_cancel": "मल्टीलाइन मोड रद्द कर दिया गया।",
        "session_reset": "सत्र रीसेट किया गया (इतिहास और फ़ाइलें साफ़ की गईं)।",
        "prefs_reset": "✓ सभी सहेजी गई प्राथमिकताएं डिफ़ॉल्ट पर रीसेट कर दी गईं।",
        "all_reset": "✓ सत्र और प्राथमिकताएं पूरी तरह से रीसेट कर दी गईं।",
        "lang_current": "सक्रिय भाषा: {flag} {name} ({code})",
        "lang_changed": "✓ भाषा बदलकर सफलतापूर्वक {flag} {name} ({code}) कर दी गई",
        "exit_msg": "llmCli बंद हो रहा है। अलविदा!",
        "unknown_cmd": "अज्ञात कमांड: '{cmd}'. उपलब्ध कमांड देखने के लिए /help टाइप करें।",
        "ambiguous_cmd": "अस्पष्ट कमांड '{cmd}'. संभावित विकल्प: {options}",
        "prompt_ai_instruction": "हमेशा स्पष्ट व्याख्या और सुव्यवस्थित कोड के साथ हिन्दी में उत्तर दें।"
    }
}


# Idioma ativo global
_active_language: str = "pt-BR"


def detect_system_language() -> str:
    """Detecta o idioma preferencial a partir das variáveis de ambiente do sistema operacional."""
    for env_var in ("LANG", "LC_ALL", "LC_MESSAGES"):
        val = os.getenv(env_var, "")
        if val:
            prefix = val.split(".")[0].replace("_", "-")
            normalized = resolve_language_code(prefix)
            if normalized != "auto":
                return normalized

    try:
        loc, _ = locale.getlocale()
        if loc:
            normalized = resolve_language_code(loc.replace("_", "-"))
            if normalized != "auto":
                return normalized
    except Exception:
        pass

    return "pt-BR"


def resolve_language_code(input_str: str) -> str:
    """Converte um nome, alias ou código de idioma para o formato canônico."""
    clean = input_str.strip().lower()
    if clean in LANGUAGE_ALIASES:
        return LANGUAGE_ALIASES[clean]
    for code in SUPPORTED_LANGUAGES:
        if code.lower() == clean or code.lower().startswith(clean):
            return code
    return "auto"


def get_active_language() -> str:
    global _active_language
    return _active_language


def set_active_language(lang_code: str) -> str:
    """Define o idioma ativo do sistema."""
    global _active_language
    resolved = resolve_language_code(lang_code)
    if resolved == "auto":
        _active_language = detect_system_language()
    else:
        _active_language = resolved
    return _active_language


def t(key: str, default: str = "", **kwargs: Any) -> str:
    """Traduz a chave indicada para o idioma ativo com interpolação de variáveis."""
    lang = get_active_language()
    translations = TRANSLATIONS.get(lang, TRANSLATIONS["pt-BR"])
    text = translations.get(key, TRANSLATIONS["en-US"].get(key, default or key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
