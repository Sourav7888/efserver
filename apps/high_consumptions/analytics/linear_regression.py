from sklearn.linear_model import LinearRegression

# @TODO: test
def get_linear_regression_model(x, y, include_test=False, include_og=False):
    """
    get linear regression model, return the model and the mean squared error
    """
    model = LinearRegression()

    # Fitting the model
    model.fit(x, y)

    data = {"model": model, "r2_score": round(model.score(x, y) * 100, 2)}

    if include_og:
        data["x"] = list(x.ravel())
        data["y"] = list(y.ravel())

    if include_test:
        data["y_test"] = list(model.predict(x).ravel())

    return data
