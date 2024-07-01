class Magazine:
    def __init__(self, id, name, category):
        self.id = id
        self._name = name
        self._category = category

    def __repr__(self):
        return f'<Magazine {self.name}>'

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value is not None and not isinstance(value, int):
            raise ValueError("ID must be an integer")
        self._id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError("Name must be a string")
        if not (2 <=len(value) <= 16):
            raise ValueError("Name must be between 2 and 16 characters")
        self._name = value

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        if not isinstance(value, str):
            raise ValueError("Category must be a string")
        if len(value) == 0:
            raise ValueError("Category must be longer than 0 characters")
        self._category = value

    @classmethod
    def create_table(cls):
        create_tables()

    @classmethod
    def drop_table(cls):
        drop_tables()

    def save(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO magazines (name, category)
            VALUES (?,?)
        """

        cursor.execute(sql, (self.name, self.category,))
        conn.commit()

        self.id = cursor.lastrowid

    @classmethod
    def create(cls, name, category):
        magazine = cls(None, name, category)
        magazine.save()

        return magazine

    def articles(self):
        from models.article import Article
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            SELECT articles.*
            FROM articles
            JOIN magazines ON articles.magazine_id = magazines.id
            WHERE magazines.id =?
        """

        cursor.execute(sql, (self.id,))
        article_rows = cursor.fetchall()

        articles = [Article(*row) for row in article_rows]
        return articles

    def contributors(self):
        from models.author import Author
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            SELECT authors.*
            FROM articles
            JOIN authors ON articles.author_id = author.id
            JOIN magazines ON articles.magazine_id = magazines.id
            WHERE magazines.id =?
        """

        cursor.execute(sql, (self.id,))
        contributor_rows = cursor.fetchall()

        contributors = [Author(*row) for row in contributor_rows]
        return contributors



    def articles_titile(self):
        articles = self.articles()
        if not articles:
            return None
        return [article.title for article in articles]

    def contributing_authors(self):
        from models.author import Author
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            SELECT authors.id, authors.name, COUNT(articles.id) as article_count
            FROM articles
            JOIN authors ON articles.author_id = authors.id
            JOIN magazines ON articles.magazine_id = magazines.id
            WHERE magazines.id = ?
            GROUP BY authors.id, authors.name
            HAVING COUNT(articles.id) > 2
        """
        cursor.execute(sql, (self.id,))
        author_rows = cursor.fetchall()

        contributing_authors = []
        for row in author_rows:
            author = Author(row[0], row[1])
            if not isinstance(author, Author):
                raise TypeError("author must be of type Author")
            contributing_authors.append(author)       
            
        return contributing_authors if contributing_authors else None

    