from sklearn.feature_extraction.text import TfidfVectorizer
from dict_matcher import TitleDictMatcher

def compare_games(game1, game2):
    game1_text = f"{game1['title']} {game1['description']}"
    game2_text = f"{game2['title']} {game2['description']}"
    text_data = [game1_text, game2_text]

    vectorizer = TfidfVectorizer()
    features = vectorizer.fit_transform(text_data)

    similarity = (features * features.T).toarray()[0][1]

    tag_similarity = len(set(game1['tags']) & set(game2['tags'])) / len(set(game1['tags']) | set(game2['tags']))
    feature_similarity = len(set(game1['features']) & set(game2['features'])) / len(set(game1['features']) | set(game2['features']))
    combined_similarity = (similarity + tag_similarity + feature_similarity) / 3

    return min(max(combined_similarity, 0), 1)
    # return similarity, feature_similarity, tag_similarity

def read_game_data(filename):
    game_data = {}
    with open(filename, 'r', encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split('\t')
            if len(parts) < 4:
                print(f"Warning: Skipping invalid line {line}")
                continue
        
            title = erase_trademark(parts[0])
            description = parts[1]
            tags_string = parts[2].strip('[]').replace("'", "")
            tags = tags_string.split(',') if tags_string else []

            features_string = parts[3].strip('[]').replace("'", "")
            features = features_string.split(',') if features_string else []

            game_data[title] = {
                "title": title,
                "description": description,
                "tags": tags,
                "features": features
            }

    return game_data

def erase_trademark(text):
  return text.replace('™', '')

def save_data(filename, pred_games, true_games, match, similarities):
    with open(filename, "a", encoding="utf-8") as f:
        if similarities:
            f.write(str(match) + "\t" + str(sum(similarities) / len(similarities)) +  "\t" +  str(max(similarities))  + "\t" + str(min(similarities)) + "\t" + ",".join(map(str, similarities))  + "\t" + ",".join(pred_games) + "\t" + ",".join(true_games) + "\n")
        else:
            f.write(str(match) + "\t" + str(match) +  "\t" +  str(match)  + "\t" + str(match) + "\t" + "0"  + "\t" + ",".join(pred_games) + "\t" + ",".join(true_games) + "\n")

if __name__ == "__main__":
    game_data = read_game_data("steam_dataset.txt")

    # game1 = "left 4 dead"
    # game2 = "left 4 dead 2"
    # similarity = compare_games(game_data[game1], game_data[game2])
    # print(f"Similarity between {game1} and {game2}: {similarity:.2f}")
    
    # exit()

    filename = "model_output.txt"
    matcher = TitleDictMatcher()

    hits = 0
    count = 0

    with open(filename, 'r', encoding="utf-8") as file:
        for line in file:
            count += 1
            parts = line.strip().split('\t')
            if len(parts) < 2:
                print(f"Warning: Skipping invalid line: {line}")
                continue
        
            text = parts[1]
            games_string = parts[0].strip('[]').replace("'", "")
            games = set(games_string.split(',') if games_string else [])

            match = 0
            similarities = []
            pred_games = []
            for pred_game, _, _ in matcher(text):
                pred_games.append(pred_game)
                if pred_game in games:
                    match = 1
                for true_game in games: 
                    if true_game in game_data and pred_game in game_data:
                        similarities.append(compare_games(game_data[true_game], game_data[pred_game]))
            
            hits += match

            save_data("output_results.txt", pred_games, games, match, similarities)
        print(f"Hits: {hits}")
        print(f"Accuracy: {hits/count*100:.4f}")
            


