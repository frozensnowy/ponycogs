# The following code fetches data about episodes from a local dataset which has data scraped from the official mlp wiki. 
# It will output an embed when the user uses `!mlp season 1 episode 1` where episode and season are obviously customized.
# The code automatically makes sure that only episodes and seasons that exist can be specified.
# Credits go to Heartshine for providing the awesome repository of pony episodes, which were named in a manner so that I could automate this.

    @commands.command(
        name="mlp",
        description="Fetches an episode of the show, and gives a direct link.",
    )
    
    async def mlp(self, context, *args):
        async def load_and_group_episodes():
            with open('mlp.json') as f:
                episodes = json.load(f)

            seasons = {}
            for episode in episodes.values():
                season = episode['season']
                if season not in seasons:
                    seasons[season] = []
                seasons[season].append(episode)
            return seasons


        input_string = ' '.join(args)
        
        # Look for the season and episode values in the input string
        match = re.search(r"season\s*(\d+)\s*episode\s*(\d+)", input_string, re.IGNORECASE)
        if match is None:
            await context.send(f"Invalid format. Please use `!mlp season <season_number> episode <episode_number>`.")
            return
        season_num = int(match.group(1))
        episode_num = int(match.group(2))

        MAX_SEASONS = 9

        # Limit the season and episode numbers
        if season_num > MAX_SEASONS:
            season_num = MAX_SEASONS
        if season_num == 3 and episode_num > 13:
            episode_num = 13
        elif episode_num > 26:
            episode_num = 26

        # Load the episode data and group them by season
        seasons = await load_and_group_episodes()

        # Look up the episode by season and episode number
        if season_num not in seasons:
            await context.send(f"Invalid season number. Please choose a season between 1 and {len(seasons)}.")
            return
        episode = next((e for e in seasons[season_num] if e['number_in_season'] == episode_num), None)
        if episode is None:
            await context.send(f"Invalid episode number. Please choose an episode between 1 and {len(seasons[season_num])}.")
            return

        # Construct the embed
        title = episode['title']
        airdate = episode['airdate']
        description = episode['synopsis']
        description = re.sub(r'\[\d+\]', '', description)  # remove blocks with digits in square brackets
        description = description.replace("\\", "").replace("\n", "")
        url = episode['url']
        thumbnail_url = episode['thumbnail_url']
        writers = episode['writers']
        writers = re.sub(r'\[\d+\]', '', writers)  # remove blocks with digits in square brackets
        storyboard = episode.get('storyboard', '')
        storyboard = re.sub(r'\[\d+\]', '', storyboard)  # remove blocks with digits in square brackets
        transcript_url = episode['transcript_url']
        gallery_url = episode['gallery_url']
        watch_now_url = f"https://static2.heartshine.gay/g4-fim/s{season_num:02d}e{episode_num:02d}-1080p.mp4"

        embed = discord.Embed(
            title=title,
            description=None,
            url=url,
            color=0xFF8C00
        )

        # Add fields to the embed
        embed.add_field(name="Season", value=season_num, inline=True)
        embed.add_field(name="Episode", value=episode_num, inline=True)
        embed.add_field(name="Airdate", value=airdate, inline=True)
        embed.add_field(name="Synopsis", value=description, inline=False)

        if transcript_url:
            embed.add_field(name="Transcript", value=f"[Click me]({transcript_url})", inline=True)

        if gallery_url:
            embed.add_field(name="Gallery", value=f"[Click me]({gallery_url})", inline=True)

        embed.add_field(name="Watch Now", value=f"[Click me]({watch_now_url})", inline=True)

        if writers and storyboard:
            embed.set_footer(text=f"Written by {writers}, storyboard by {storyboard}")
        elif writers:
            embed.set_footer(text=f"Written by {writers}")
        elif storyboard:
            embed.set_footer(text=f"Storyboard by {storyboard}")

        embed.set_image(url=thumbnail_url)

        await context.send(embed=embed)
