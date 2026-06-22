TypedDict je typová anotace pro slovník, která říká, jaké klíče a typy hodnot má obsahovat (např. {"message": str}), ale za běhu je to stále normální dict. 

TypedDict slouží jen pro typovou kontrolu (editor/mypy) - odhalí typo v klíči (state["mesage"]) nebo špatný typ hodnoty. Za běhu se s ním zachází úplně stejně jako s obyčejným dict (state["message"]), žádnou validaci ani dot-notaci (state.message) to nepřidává.
